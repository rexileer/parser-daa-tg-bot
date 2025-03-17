from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.BigIntegerField(unique=True)  # Telegram ID пользователя
    monitoring_enabled = models.BooleanField(default=False)  # Включен ли мониторинг

    def __str__(self):
        return f"{self.user_id} - {'Вкл' if self.monitoring_enabled else 'Выкл'}"
    
    class Meta:
        verbose_name = "Пользователь Telegram"
        verbose_name_plural = "Пользователи Telegram"


class UserFilters(models.Model):
    user_id = models.BigIntegerField(unique=True)  # Telegram ID пользователя
    platform = models.CharField(max_length=50, blank=True, null=True)  # Площадка
    price = models.CharField(max_length=50, blank=True, null=True)  # Цена
    brand = models.CharField(max_length=50, blank=True, null=True)  # Марка
    engine = models.CharField(max_length=50, blank=True, null=True)  # Двигатель
    mileage = models.CharField(max_length=50, blank=True, null=True)  # Пробег
    gearbox = models.CharField(max_length=50, blank=True, null=True)  # Коробка передач
    owners = models.CharField(max_length=50, blank=True, null=True)  # Кол-во владельцев
    condition = models.CharField(max_length=50, blank=True, null=True)  # Состояние
    seller = models.CharField(max_length=50, blank=True, null=True)  # Продавец
    city = models.CharField(max_length=50, blank=True, null=True)  # Город
    year = models.CharField(max_length=50, blank=True, null=True)  # Год выпуска
    body_type = models.CharField(max_length=50, blank=True, null=True)  # Тип кузова
    color = models.CharField(max_length=50, blank=True, null=True)  # Цвет кузова
    drive = models.CharField(max_length=50, blank=True, null=True)  # Привод
    steering = models.CharField(max_length=50, blank=True, null=True)  # Руль
    ad_type = models.CharField(max_length=50, blank=True, null=True)  # Тип объявлений

    class Meta:
        verbose_name = "Фильтр пользователя"
        verbose_name_plural = "Фильтры пользователей"

    def __str__(self):
        return f"Фильтры пользователя {self.user_id}"
