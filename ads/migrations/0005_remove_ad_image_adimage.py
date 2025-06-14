# Generated by Django 5.1.6 on 2025-02-27 08:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0004_alter_ad_mileage_alter_ad_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ad',
            name='image',
        ),
        migrations.CreateModel(
            name='AdImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='ads/')),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='ads.ad')),
            ],
        ),
    ]
