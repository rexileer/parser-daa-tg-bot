from django.db import models
from django.utils.timezone import now

class StartCommandResponse(models.Model):
    text = models.TextField()

    def save(self, *args, **kwargs):
        if StartCommandResponse.objects.exists():
            # Разрешаем обновлять только первую запись
            self.pk = StartCommandResponse.objects.first().pk
        super().save(*args, **kwargs)

    def __str__(self):
        return "Приветственное сообщение"
    
    class Meta:
        verbose_name = 'Приветственное сообщение'
        verbose_name_plural = 'Приветственное сообщение'

class ViewAllAdsResponse(models.Model):
    text = models.TextField()

    def save(self, *args, **kwargs):
        if ViewAllAdsResponse.objects.exists():
            self.pk = ViewAllAdsResponse.objects.first().pk
        super().save(*args, **kwargs)
    
    def __str__(self):
        return "Сообщение для просмотра всех объявлений"
    
    class Meta:
        verbose_name = 'Сообщение для просмотра всех объявлений'
        verbose_name_plural = 'Сообщение для просмотра всех объявлений'



class BroadcastMessage(models.Model):
    text = models.TextField("Текст сообщения", blank=True, null=True)
    file = models.FileField("Медиафайл", upload_to="media/", blank=True, null=True)
    media_type = models.CharField(
        "Тип медиафайла",
        max_length=10,
        choices=[("image", "Изображение"), ("video", "Видео")],
        blank=True,
        null=True,
    )
    send_time = models.DateTimeField("Время отправки", default=now)
    is_sent = models.BooleanField("Отправлено", default=False)

    def __str__(self):
        return f"Рассылка {self.id} на {self.send_time}"
    
    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
