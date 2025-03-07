from django.contrib import admin
from .models import User, UserFilters

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "name", "monitoring_enabled")  # Отображение в админке
    list_filter = ("monitoring_enabled",)  # Фильтр по статусу мониторинга
    search_fields = ("user_id", "name")  # Поиск по ID и имени
    

@admin.register(UserFilters)
class UserFiltersAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'platform', 'price', 'brand', 'engine', 'mileage', 'gearbox', 'owners', 'condition', 'seller', 'city', 'year', 'body_type', 'color', 'drive', 'steering', 'ad_type')
    search_fields = ('user_id', 'platform', 'price', 'brand', 'engine', 'city')
    list_filter = ('platform', 'brand', 'city', 'year', 'body_type', 'drive')  # Вы можете настроить фильтры по своим полям
