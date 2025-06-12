from django.contrib import admin
from .models import Advertisement

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('platform', 'brand', 'model', 'price', 'city', 'year', 'created_at')
    list_filter = ('platform', 'brand', 'city', 'body_type', 'engine', 'gearbox', 'drive')
    search_fields = ('name', 'brand', 'model', 'city')
    readonly_fields = ('ad_id', 'created_at', 'published_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Идентификация', {
            'fields': ('ad_id', 'platform', 'link')
        }),
        ('Основная информация', {
            'fields': ('name', 'brand', 'model', 'year', 'price', 'city', 'image')
        }),
        ('Характеристики автомобиля', {
            'fields': ('mileage', 'engine', 'color', 'gearbox', 'drive', 'steering', 
                      'owners', 'body_type', 'condition')
        }),
        ('Информация об объявлении', {
            'fields': ('ad_type', 'seller', 'created_at', 'published_at')
        }),
    )
