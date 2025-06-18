from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Advertisement
from .forms import AdvertisementFilterForm
from datetime import datetime, timedelta

def index(request):
    """
    View for the main page with advertisements and filtering
    """
    # Get all advertisements
    advertisements = Advertisement.objects.all().order_by('-published_at')
    
    # Get selected platforms from request
    selected_platforms = request.GET.getlist('platform')
    
    # Apply filters
    form = AdvertisementFilterForm(request.GET)
    if form.is_valid():
        # Platform filter
        platform = form.cleaned_data.get('platform')
        if platform:
            advertisements = advertisements.filter(platform__in=platform)
        
        # Brand filter
        brand = form.cleaned_data.get('brand')
        if brand:
            # Changed from iexact to icontains to match partial brand names
            advertisements = advertisements.filter(brand__icontains=brand)
        
        # City filter (case-insensitive partial match)
        city = form.cleaned_data.get('city')
        city_select = form.cleaned_data.get('city_select')
        
        # Create a filter for city (from either text input or dropdown)
        city_filter = Q()
        if city:
            city_filter |= Q(city__icontains=city)
        if city_select:
            city_filter |= Q(city__icontains=city_select)
        
        # Apply city filter if any city criteria was provided
        if city or city_select:
            advertisements = advertisements.filter(city_filter)
        
        # Price filters
        price_range = form.cleaned_data.get('price_range')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        
        if price_range:
            min_price, max_price = price_range.split('-')
            min_price = int(min_price) if min_price else None
            max_price = int(max_price) if max_price else None
            
            if min_price is not None and max_price is not None:
                advertisements = advertisements.filter(price__range=(min_price, max_price))
            elif min_price is not None:
                advertisements = advertisements.filter(price__gte=min_price)
            elif max_price is not None:
                advertisements = advertisements.filter(price__lte=max_price)
        elif price_min is not None or price_max is not None:
            if price_min is not None:
                advertisements = advertisements.filter(price__gte=price_min)
            if price_max is not None:
                advertisements = advertisements.filter(price__lte=price_max)
        
        # Year filters
        year_min = form.cleaned_data.get('year_min')
        year_max = form.cleaned_data.get('year_max')
        
        if year_min or year_max:
            # Convert year as string to int for comparison
            if year_min:
                year_min_str = str(year_min)
                advertisements = advertisements.filter(
                    Q(year__gte=year_min_str) | Q(year__regex=r'^\d{4}', year__gte=year_min_str)
                )
            if year_max:
                year_max_str = str(year_max)
                advertisements = advertisements.filter(
                    Q(year__lte=year_max_str) | Q(year__regex=r'^\d{4}', year__lte=year_max_str)
                )
        
        # Mileage filter
        mileage_range = form.cleaned_data.get('mileage_range')
        if mileage_range:
            min_mileage, max_mileage = mileage_range.split('-')
            min_mileage = int(min_mileage) if min_mileage else None
            max_mileage = int(max_mileage) if max_mileage else None
            
            if min_mileage is not None and max_mileage is not None:
                advertisements = advertisements.filter(mileage__range=(min_mileage, max_mileage))
            elif min_mileage is not None:
                advertisements = advertisements.filter(mileage__gte=min_mileage)
            elif max_mileage is not None:
                advertisements = advertisements.filter(mileage__lte=max_mileage)
        
        # Car details filters - changed all to icontains for partial matching
        body_type = form.cleaned_data.get('body_type')
        if body_type:
            advertisements = advertisements.filter(body_type__icontains=body_type)
            
        engine = form.cleaned_data.get('engine')
        if engine:
            advertisements = advertisements.filter(engine__icontains=engine)
            
        gearbox = form.cleaned_data.get('gearbox')
        if gearbox:
            advertisements = advertisements.filter(gearbox__icontains=gearbox)
            
        drive = form.cleaned_data.get('drive')
        if drive:
            advertisements = advertisements.filter(drive__icontains=drive)
            
        steering = form.cleaned_data.get('steering')
        if steering:
            advertisements = advertisements.filter(steering__icontains=steering)
            
        color = form.cleaned_data.get('color')
        if color:
            # Handle both 'е' and 'ё' variants in color names
            # Create a Q object for the partial lowercase match
            color_filter = Q(color__icontains=color)
            # Add another condition for the alternative spelling
            if 'е' in color:
                alt_color = color.replace('е', 'ё')
                color_filter |= Q(color__icontains=alt_color)
            elif 'ё' in color:
                alt_color = color.replace('ё', 'е')
                color_filter |= Q(color__icontains=alt_color)
            
            advertisements = advertisements.filter(color_filter)
            
        seller = form.cleaned_data.get('seller')
        if seller:
            advertisements = advertisements.filter(seller__icontains=seller)
        
        # Date filters
        date_min = form.cleaned_data.get('date_min')
        date_max = form.cleaned_data.get('date_max')
        
        if date_min:
            advertisements = advertisements.filter(published_at__date__gte=date_min)
        
        if date_max:
            # Include the whole day
            next_day = date_max + timedelta(days=1)
            advertisements = advertisements.filter(published_at__date__lt=next_day)
    
    # Paginate results
    paginator = Paginator(advertisements, 24)  # 24 ads per page
    page = request.GET.get('page')
    try:
        ads_page = paginator.page(page)
    except PageNotAnInteger:
        ads_page = paginator.page(1)
    except EmptyPage:
        ads_page = paginator.page(paginator.num_pages)
    
    # Stats for displaying on the page
    stats = {
        'total_ads': advertisements.count(),
        'unique_brands': advertisements.values_list('brand', flat=True).distinct().count(),
        'price_range': {
            'min': advertisements.order_by('price').first().price if advertisements else 0,
            'max': advertisements.order_by('-price').first().price if advertisements else 0,
        }
    }
    
    return render(request, 'ads/index.html', {
        'form': form,
        'advertisements': ads_page,
        'stats': stats,
        'selected_platforms': selected_platforms,
    })

def ad_detail(request, ad_id):
    """
    View for a single advertisement
    """
    ad = Advertisement.objects.get(ad_id=ad_id)
    return render(request, 'ads/detail.html', {'ad': ad})
