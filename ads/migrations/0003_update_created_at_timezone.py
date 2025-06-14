from django.db import migrations
from django.utils import timezone


def update_created_at_with_timezone(apps, schema_editor):
    """
    Update existing Advertisement records to use timezone-aware datetimes
    """
    Advertisement = apps.get_model('ads', 'Advertisement')
    for ad in Advertisement.objects.all():
        if not ad.created_at.tzinfo:  # If timezone info is not present
            ad.created_at = timezone.make_aware(ad.created_at)
            ad.save(update_fields=['created_at'])


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0002_alter_advertisement_created_at'),
    ]

    operations = [
        migrations.RunPython(update_created_at_with_timezone, migrations.RunPython.noop),
    ] 