# Generated by Django 5.1.6 on 2025-02-26 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0003_rename_brand_ad_mark_names'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='mileage',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='ad',
            name='price',
            field=models.PositiveIntegerField(),
        ),
    ]
