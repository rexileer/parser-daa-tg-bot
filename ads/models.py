from django.db import models
import json
from datetime import datetime
from django.utils import timezone

class Advertisement(models.Model):
    PLATFORM_CHOICES = [
        ('avito', 'Avito'),
        ('drom', 'Drom'),
        ('autoru', 'Auto.ru'),
    ]
    
    # Identification
    ad_id = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    link = models.URLField(max_length=500)
    
    # Basic info
    name = models.CharField(max_length=500)
    brand = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    year = models.CharField(max_length=20, null=True, blank=True)
    price = models.IntegerField(default=0)
    city = models.CharField(max_length=200)
    image = models.URLField(max_length=500, null=True, blank=True)
    
    # Car details
    mileage = models.IntegerField(null=True, blank=True)
    engine = models.CharField(max_length=200, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    gearbox = models.CharField(max_length=100, null=True, blank=True)
    drive = models.CharField(max_length=100, null=True, blank=True)
    steering = models.CharField(max_length=100, null=True, blank=True)
    owners = models.CharField(max_length=50, null=True, blank=True)
    body_type = models.CharField(max_length=100, null=True, blank=True)
    condition = models.CharField(max_length=100, null=True, blank=True)
    
    # Type and seller
    ad_type = models.CharField(max_length=100, null=True, blank=True)
    seller = models.CharField(max_length=200, null=True, blank=True)
    
    # Timestamps - changed from auto_now_add to manually set in save method
    created_at = models.DateTimeField()
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['brand']),
            models.Index(fields=['city']),
            models.Index(fields=['platform']),
            models.Index(fields=['price']),
            models.Index(fields=['published_at']),
        ]
    
    def save(self, *args, **kwargs):
        # Set created_at with timezone-aware datetime if it's a new object
        if not self.pk:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.platform} - {self.brand} {self.model} ({self.price} ₽)"
    
    @classmethod
    def from_redis_data(cls, ad_id, ad_data):
        """
        Create or update an Advertisement instance from Redis data
        """
        try:
            ad_dict = json.loads(ad_data) if isinstance(ad_data, str) else ad_data
            
            # Check if ad already exists
            try:
                ad = cls.objects.get(ad_id=ad_id)
                # Update existing ad
                ad.platform = ad_dict.get('platform', '')
                ad.link = ad_dict.get('link', '')
                ad.name = ad_dict.get('name', '')
                ad.brand = ad_dict.get('brand', '')
                ad.model = ad_dict.get('model', '')
                ad.year = ad_dict.get('year', '')
                ad.price = int(ad_dict.get('price', 0)) if ad_dict.get('price', 0) != 'unknown' else 0
                ad.city = ad_dict.get('city', '')
                ad.image = ad_dict.get('image', '')
                ad.mileage = int(ad_dict.get('mileage', 0)) if ad_dict.get('mileage', 0) != 'unknown' else None
                ad.engine = ad_dict.get('engine', '')
                ad.color = ad_dict.get('color', '')
                ad.gearbox = ad_dict.get('gearbox', '')
                ad.drive = ad_dict.get('drive', '')
                ad.steering = ad_dict.get('steering', '')
                ad.owners = ad_dict.get('owners', '')
                ad.body_type = ad_dict.get('body_type', '')
                ad.condition = ad_dict.get('condition', '')
                ad.ad_type = ad_dict.get('ad_type', '')
                ad.seller = ad_dict.get('seller', '')
                ad.published_at = timezone.now()
                ad.save()
                return ad
            except cls.DoesNotExist:
                # Create new ad with timezone-aware datetime
                ad = cls(
                    ad_id=ad_id,
                    platform=ad_dict.get('platform', ''),
                    link=ad_dict.get('link', ''),
                    name=ad_dict.get('name', ''),
                    brand=ad_dict.get('brand', ''),
                    model=ad_dict.get('model', ''),
                    year=ad_dict.get('year', ''),
                    price=int(ad_dict.get('price', 0)) if ad_dict.get('price', 0) != 'unknown' else 0,
                    city=ad_dict.get('city', ''),
                    image=ad_dict.get('image', ''),
                    mileage=int(ad_dict.get('mileage', 0)) if ad_dict.get('mileage', 0) != 'unknown' else None,
                    engine=ad_dict.get('engine', ''),
                    color=ad_dict.get('color', ''),
                    gearbox=ad_dict.get('gearbox', ''),
                    drive=ad_dict.get('drive', ''),
                    steering=ad_dict.get('steering', ''),
                    owners=ad_dict.get('owners', ''),
                    body_type=ad_dict.get('body_type', ''),
                    condition=ad_dict.get('condition', ''),
                    ad_type=ad_dict.get('ad_type', ''),
                    seller=ad_dict.get('seller', ''),
                    created_at=timezone.now(),
                    published_at=timezone.now(),
                )
                ad.save()
                return ad
        except Exception as e:
            print(f"Error creating/updating advertisement from Redis data: {e}")
            return None
