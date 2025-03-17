from django.contrib import admin
from django.utils.html import format_html
from .models import Parser

admin.site.site_header = "Парсеры"

@admin.register(Parser)
class ParserAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "status")  
    list_filter = ("is_active",)
    search_fields = ("name", "url")

    def status(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green; font-weight: bold;">🟢 Включен</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">🔴 Выключен</span>')

    status.short_description = "Статус"
