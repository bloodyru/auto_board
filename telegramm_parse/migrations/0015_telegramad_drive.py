# Generated by Django 5.1.6 on 2025-03-27 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegramm_parse', '0014_telegramad_seller'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramad',
            name='drive',
            field=models.CharField(choices=[('front', 'Передний'), ('rear', 'Задний'), ('4x4', 'Полный')], default='front', max_length=7),
        ),
    ]
