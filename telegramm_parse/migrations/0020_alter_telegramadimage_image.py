# Generated by Django 5.1.6 on 2025-03-31 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegramm_parse', '0019_alter_telegramadimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramadimage',
            name='image',
            field=models.TextField(),
        ),
    ]
