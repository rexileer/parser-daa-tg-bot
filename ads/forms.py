from django import forms
from .models import Advertisement

class AdvertisementFilterForm(forms.Form):
    PRICE_CHOICES = [
        ('', 'Любая цена'),
        ('0-500000', 'до 500 000 ₽'),
        ('500000-1000000', '500 000 - 1 000 000 ₽'),
        ('1000000-1500000', '1 000 000 - 1 500 000 ₽'),
        ('1500000-2000000', '1 500 000 - 2 000 000 ₽'),
        ('2000000-3000000', '2 000 000 - 3 000 000 ₽'),
        ('3000000-0', 'от 3 000 000 ₽'),
    ]
    
    MILEAGE_CHOICES = [
        ('', 'Любой пробег'),
        ('0-10000', 'до 10 000 км'),
        ('10000-50000', '10 000 - 50 000 км'),
        ('50000-100000', '50 000 - 100 000 км'),
        ('100000-150000', '100 000 - 150 000 км'),
        ('150000-0', 'от 150 000 км'),
    ]
    
    # Get unique values for dynamic dropdowns
    @staticmethod
    def get_unique_values(field):
        # Get all distinct values for the field
        values = Advertisement.objects.values_list(field, flat=True).distinct()
        
        # Process values: convert to lowercase, replace 'ё' with 'е', filter out empty values
        normalized_values = []
        for v in values:
            if v and v != 'unknown':
                # Convert to lowercase and replace ё with е
                normalized_v = v.lower().replace('ё', 'е')
                normalized_values.append(normalized_v)
        
        # Remove duplicates using set
        unique_values = list(set(normalized_values))
        
        # Sort the values
        unique_values.sort()
        
        # Format as (value, value) tuples for form choices with proper capitalization
        return [(v, v.capitalize()) for v in unique_values]
    
    # Search fields
    city = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите город'})
    )
    
    city_select = forms.ChoiceField(
        required=False,
        choices=[('', 'Выберите город')],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Filter fields
    platform = forms.MultipleChoiceField(
        required=False,
        choices=[('avito', 'Avito'), ('drom', 'Drom'), ('autoru', 'Auto.ru')],
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    
    brand = forms.ChoiceField(
        required=False,
        choices=[('', 'Все марки')],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    price_range = forms.ChoiceField(
        required=False,
        choices=PRICE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    price_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'От'})
    )
    
    price_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'До'})
    )
    
    year_min = forms.IntegerField(
        required=False,
        min_value=1900,
        max_value=2100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'От'})
    )
    
    year_max = forms.IntegerField(
        required=False,
        min_value=1900,
        max_value=2100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'До'})
    )
    
    mileage_range = forms.ChoiceField(
        required=False,
        choices=MILEAGE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    body_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Любой тип кузова')],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    engine = forms.ChoiceField(
        required=False,
        choices=[('', 'Любой двигатель')],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    gearbox = forms.ChoiceField(
        required=False,
        choices=[('', 'Любая КПП')],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    drive = forms.ChoiceField(
        required=False,
        choices=[('', 'Любой привод')],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    steering = forms.ChoiceField(
        required=False,
        choices=[('', 'Любой руль')],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    color = forms.ChoiceField(
        required=False,
        choices=[('', 'Любой цвет')],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    seller = forms.ChoiceField(
        required=False,
        choices=[('', 'Любой тип продавца')],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_min = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    date_max = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate dynamic choices
        self.fields['brand'].choices = [('', 'Все марки')] + self.get_unique_values('brand')
        self.fields['body_type'].choices = [('', 'Любой тип кузова')] + self.get_unique_values('body_type')
        self.fields['engine'].choices = [('', 'Любой двигатель')] + self.get_unique_values('engine')
        self.fields['gearbox'].choices = [('', 'Любая КПП')] + self.get_unique_values('gearbox')
        self.fields['drive'].choices = [('', 'Любой привод')] + self.get_unique_values('drive')
        self.fields['steering'].choices = [('', 'Любой руль')] + self.get_unique_values('steering')
        self.fields['color'].choices = [('', 'Любой цвет')] + self.get_unique_values('color')
        self.fields['seller'].choices = [('', 'Любой тип продавца')] + self.get_unique_values('seller')
        self.fields['city_select'].choices = [('', 'Выберите город')] + self.get_unique_values('city') 