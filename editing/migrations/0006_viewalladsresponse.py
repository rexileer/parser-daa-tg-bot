# Generated by Django 5.1.6 on 2025-06-14 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editing', '0005_remove_broadcastmessage_image_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewAllAdsResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
            options={
                'verbose_name': 'Сообщение для просмотра всех объявлений',
                'verbose_name_plural': 'Сообщение для просмотра всех объявлений',
            },
        ),
    ]
