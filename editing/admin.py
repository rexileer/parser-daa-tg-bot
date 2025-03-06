from django.contrib import admin
from .models import StartCommandResponse

@admin.register(StartCommandResponse)
class StartCommandResponseAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not StartCommandResponse.objects.exists()  # Разрешаем добавлять, только если нет записей

    def has_delete_permission(self, request, obj=None):
        return False  # Запрещаем удаление
