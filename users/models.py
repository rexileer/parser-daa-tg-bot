from django.db import models
from django.contrib.postgres.fields import ArrayField

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
    platform = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Площадка
    price = models.CharField(max_length=50, blank=True, null=True)  # Цена
    brand = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Марка
    engine = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Двигатель
    mileage = models.CharField(max_length=50, blank=True, null=True)  # Пробег
    gearbox = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Коробка передач
    owners = models.CharField(max_length=50, blank=True, null=True)  # Кол-во владельцев
    condition = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Состояние
    seller = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Продавец
    city = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Город
    year = models.CharField(max_length=50, blank=True, null=True)  # Год выпуска
    body_type = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Тип кузова
    color = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Цвет кузова
    drive = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Привод
    steering = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Руль
    ad_type = ArrayField(models.CharField(max_length=50, blank=True), blank=True, default=list)  # Тип объявлений

    class Meta:
        verbose_name = "Фильтр пользователя"
        verbose_name_plural = "Фильтры пользователей"

    def __str__(self):
        return f"Фильтры пользователя {self.user_id}"
