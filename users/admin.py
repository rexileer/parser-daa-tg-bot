from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "name", "monitoring_enabled")  # Отображение в админке
    list_filter = ("monitoring_enabled",)  # Фильтр по статусу мониторинга
    search_fields = ("user_id", "name")  # Поиск по ID и имени