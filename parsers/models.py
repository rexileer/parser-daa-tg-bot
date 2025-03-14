from django.db import models
from asgiref.sync import sync_to_async

class Parser(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Уникальное имя
    url = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Парсер"
        verbose_name_plural = "Парсеры"
        ordering = ["name"]  # Упорядочивание по алфавиту

    def __str__(self):
        status = "🟢" if self.is_active else "🔴"
        return f"{status} {self.name}"
    
    @classmethod
    async def get_active_parsers(cls):
        return await sync_to_async(list)(cls.objects.filter(is_active=True))
