from django.contrib import admin
from .models import StartCommandResponse, BroadcastMessage
from django.utils.html import format_html
from django.db import models
from django.forms import FileInput


admin.site.site_header = "Редактирование"

@admin.register(StartCommandResponse)
class StartCommandResponseAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not StartCommandResponse.objects.exists()  # Разрешаем добавлять, только если нет записей

    def has_delete_permission(self, request, obj=None):
        return False  # Запрещаем удаление



@admin.register(BroadcastMessage)
class BroadcastMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "send_time", "is_sent", "media_display")
    list_filter = ("is_sent",)
    ordering = ("send_time",)
    readonly_fields = ("media_preview",)

    formfield_overrides = {
        models.FileField: {"widget": FileInput(attrs={"accept": "image/*,video/*"})},
    }

    def media_display(self, obj):
        """Предпросмотр медиа в списке рассылок"""
        if obj.file:
            if obj.media_type == "image":
                return format_html('<img src="{}" style="max-height: 100px; max-width: 150px;" />', obj.file.url)
            elif obj.media_type == "video":
                return format_html('<video width="150" height="100" controls><source src="{}" type="video/mp4"></video>', obj.file.url)
        return "Нет медиа"

    media_display.short_description = "Медиа"

    def media_preview(self, obj):
        """Предпросмотр медиа в форме редактирования"""
        if obj.file:
            if obj.media_type == "image":
                return format_html('<img src="{}" style="max-width: 300px; max-height: 300px; margin-top: 10px;" />', obj.file.url)
            elif obj.media_type == "video":
                return format_html('<video width="300" height="200" controls style="margin-top: 10px;"><source src="{}" type="video/mp4"></video>', obj.file.url)
        return "Нет медиафайла"

    media_preview.short_description = "Предпросмотр медиа"
