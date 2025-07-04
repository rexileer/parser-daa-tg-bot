# Generated by Django 5.1.6 on 2025-06-12 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad_id', models.CharField(max_length=255, unique=True)),
                ('platform', models.CharField(choices=[('avito', 'Avito'), ('drom', 'Drom'), ('autoru', 'Auto.ru')], max_length=20)),
                ('link', models.URLField()),
                ('name', models.CharField(max_length=255)),
                ('brand', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('year', models.CharField(blank=True, max_length=20, null=True)),
                ('price', models.IntegerField(default=0)),
                ('city', models.CharField(max_length=100)),
                ('image', models.URLField(blank=True, null=True)),
                ('mileage', models.IntegerField(blank=True, null=True)),
                ('engine', models.CharField(blank=True, max_length=100, null=True)),
                ('color', models.CharField(blank=True, max_length=50, null=True)),
                ('gearbox', models.CharField(blank=True, max_length=50, null=True)),
                ('drive', models.CharField(blank=True, max_length=50, null=True)),
                ('steering', models.CharField(blank=True, max_length=50, null=True)),
                ('owners', models.CharField(blank=True, max_length=20, null=True)),
                ('body_type', models.CharField(blank=True, max_length=50, null=True)),
                ('condition', models.CharField(blank=True, max_length=50, null=True)),
                ('ad_type', models.CharField(blank=True, max_length=50, null=True)),
                ('seller', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Объявление',
                'verbose_name_plural': 'Объявления',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['brand'], name='ads_adverti_brand_8ca683_idx'), models.Index(fields=['city'], name='ads_adverti_city_3465e8_idx'), models.Index(fields=['platform'], name='ads_adverti_platfor_cee0b2_idx'), models.Index(fields=['price'], name='ads_adverti_price_d1337e_idx'), models.Index(fields=['published_at'], name='ads_adverti_publish_68823e_idx')],
            },
        ),
    ]
