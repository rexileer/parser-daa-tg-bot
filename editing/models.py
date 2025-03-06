from django.db import models

class StartCommandResponse(models.Model):
    text = models.TextField()

    def save(self, *args, **kwargs):
        if StartCommandResponse.objects.exists():
            # Разрешаем обновлять только первую запись
            self.pk = StartCommandResponse.objects.first().pk
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text[:50]
