from django.contrib import admin
from .models import StartCommandResponse, BroadcastMessage

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

    # Метод для отображения медиафайлов (если есть фото или видео)
    def media_display(self, obj):
        if obj.video:
            return f"Видео: {obj.video.name}"  # Если есть видео, показываем его
        elif obj.image:
            return f"Фото: {obj.image.name}"  # Если есть только фото, показываем его
        return "Нет медиа"  # Если нет медиа, показываем, что медиа отсутствует
    
    media_display.short_description = 'Медиафайл'

    # Описание полей, чтобы администратор понимал, что если оба медиа (фото и видео), то отправляется только видео
    fieldsets = (
        (None, {
            'fields': ('text', 'send_time', 'is_sent', 'image', 'video')
        }),
    )

    # Метод для отображения подсказки в админке
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and (obj.image and obj.video):
            fieldsets[0][1]['description'] = 'Если присутствуют фото и видео, будет отправлено только видео.'
        return fieldsets

    
    