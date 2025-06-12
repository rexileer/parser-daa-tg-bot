from django.db import models
import json
from datetime import datetime

class Advertisement(models.Model):
    PLATFORM_CHOICES = [
        ('avito', 'Avito'),
        ('drom', 'Drom'),
        ('autoru', 'Auto.ru'),
    ]
    
    # Identification
    ad_id = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    link = models.URLField()
    
    # Basic info
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.CharField(max_length=20, null=True, blank=True)
    price = models.IntegerField(default=0)
    city = models.CharField(max_length=100)
    image = models.URLField(null=True, blank=True)
    
    # Car details
    mileage = models.IntegerField(null=True, blank=True)
    engine = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    gearbox = models.CharField(max_length=50, null=True, blank=True)
    drive = models.CharField(max_length=50, null=True, blank=True)
    steering = models.CharField(max_length=50, null=True, blank=True)
    owners = models.CharField(max_length=20, null=True, blank=True)
    body_type = models.CharField(max_length=50, null=True, blank=True)
    condition = models.CharField(max_length=50, null=True, blank=True)
    
    # Type and seller
    ad_type = models.CharField(max_length=50, null=True, blank=True)
    seller = models.CharField(max_length=100, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
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
    
    def __str__(self):
        return f"{self.platform} - {self.brand} {self.model} ({self.price} ₽)"
    
    @classmethod
    def from_redis_data(cls, ad_id, ad_data):
        """
        Create or update an Advertisement instance from Redis data
        """
        try:
            ad_dict = json.loads(ad_data) if isinstance(ad_data, str) else ad_data
            
            # Try to get existing ad or create a new one
            ad, created = cls.objects.update_or_create(
                ad_id=ad_id,
                defaults={
                    'platform': ad_dict.get('platform', ''),
                    'link': ad_dict.get('link', ''),
                    'name': ad_dict.get('name', ''),
                    'brand': ad_dict.get('brand', ''),
                    'model': ad_dict.get('model', ''),
                    'year': ad_dict.get('year', ''),
                    'price': int(ad_dict.get('price', 0)) if ad_dict.get('price', 0) != 'unknown' else 0,
                    'city': ad_dict.get('city', ''),
                    'image': ad_dict.get('image', ''),
                    'mileage': int(ad_dict.get('mileage', 0)) if ad_dict.get('mileage', 0) != 'unknown' else None,
                    'engine': ad_dict.get('engine', ''),
                    'color': ad_dict.get('color', ''),
                    'gearbox': ad_dict.get('gearbox', ''),
                    'drive': ad_dict.get('drive', ''),
                    'steering': ad_dict.get('steering', ''),
                    'owners': ad_dict.get('owners', ''),
                    'body_type': ad_dict.get('body_type', ''),
                    'condition': ad_dict.get('condition', ''),
                    'ad_type': ad_dict.get('ad_type', ''),
                    'seller': ad_dict.get('seller', ''),
                    'published_at': datetime.now(),
                }
            )
            return ad
        except Exception as e:
            print(f"Error creating/updating advertisement from Redis data: {e}")
            return None
