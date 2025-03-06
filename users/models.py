from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.BigIntegerField(unique=True)  # Telegram ID пользователя
    monitoring_enabled = models.BooleanField(default=False)  # Включен ли мониторинг

    def __str__(self):
        return f"{self.user_id} - {'Вкл' if self.monitoring_enabled else 'Выкл'}"
