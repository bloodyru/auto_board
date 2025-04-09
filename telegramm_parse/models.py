from django.db import models
from django.contrib.auth import get_user_model
from ads.country_choices import COUNTRY_CHOICES
from PIL import Image
from django.core.files import File
from io import BytesIO
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

User = get_user_model()

class TelegramAd(models.Model):
    FUEL_TYPE_CHOICES = [
        ("petrol", "Бензин"),
        ("diesel", "Дизель"),
        ("gas", "Газ"),
        ("electric", "Электро"),
        ("hybrid", "Гибрид"),
    ]

    GEARBOX_TYPE_CHOICES = [
        ("automatic", "Автомат"),
        ("machanical", "Механика"),
    ]

    BODY_TYPE_CHOICES = [
        ("sedan", "Седан"),
        ("hatchback", "Хэтчбек"),
        ("suv", "Внедорожник"),
        ("station_wagon", "Универсал"),
        ("minivan", "Минивэн"),
        ("pickup", "Пикап"),
        ("limousine", "Лимузин"),
        ("van", "Фургон"),
        ("convertible", "Кабриолет"),
    ]

    SELLER_TYPE_CHOICES = [
        ("private", "Частник"),
        ("company", "Компания"),
    ]

    DRIVE_TYPE_CHOICES = [
        ("front", "Передний"),
        ("rear", "Задний"),
        ("4x4", "Полный"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("pending", "Pending"),
        ("sold", "Sold"),
    ]

    LOCATION_CHOICES = [
        ("in_stock", "В наличии"),
        ("in_transit", "В пути"),
        ("on_order", "Под заказ"),
    ]

    DAMAGED_CHOICES = [
        ("ok", "Целая/На ходу"),
        ("damaged", "Битая/Не на ходу"),
    ]

    STEERING_CHOICES = [
        ("left", "Левый"),
        ("right", "Правый"),
    ]

    COLOR_CHOICES = [
        ("black", "Черный"),
        ("gray", "Серый"),
        ("white", "Белый"),
        ("blue", "Синий"),
        ("red", "Красный"),
        ("green", "Зеленый"),
        ("orange", "Оранжевый"),
        ("yellow", "Желтый"),
    ]

    DOCUMENTS_CHOICES = [
        ("ok", "В порядке"),
        ("bad", "Нет/проблемные"),
    ]

    message_id = models.BigIntegerField(unique=True)
    description = models.TextField()
    date_posted = models.DateTimeField()
    mark_names = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    mileage = models.PositiveIntegerField(blank=True, null=True)
    price = models.PositiveIntegerField(blank=True, null=True)  # Добавили цену
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=8, default="telegram")
    link = models.URLField(max_length=300, blank=True, null=True)
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPE_CHOICES, default="petrol", blank=True,
        null=True,
        verbose_name="Любое топливо")
    gearbox = models.CharField(max_length=10, choices=GEARBOX_TYPE_CHOICES, default="machanical")
    body_type = models.CharField(max_length=15, choices=BODY_TYPE_CHOICES, default="sedan")
    exchange = models.BooleanField( default=False, verbose_name="Обмен", help_text="Отметьте, если хотите обмен авто")
    seller = models.CharField(max_length=7, choices=SELLER_TYPE_CHOICES, default="private")
    drive = models.CharField(max_length=7, choices=DRIVE_TYPE_CHOICES, default="front")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    location = models.CharField( max_length=10, choices=LOCATION_CHOICES, default="in_stock", blank=True, verbose_name="Статус наличия")
    damaged = models.CharField(max_length=10, choices=DAMAGED_CHOICES, default="ok", verbose_name="Состояние")
    steering = models.CharField( max_length=5, choices=STEERING_CHOICES, default="left", verbose_name="Руль")
    color = models.CharField( max_length=20, choices=COLOR_CHOICES, verbose_name="Цвет", default="white",)
    documents = models.CharField(max_length=20, choices=DOCUMENTS_CHOICES, verbose_name="Документы", default="ok", )
    country = models.CharField( max_length=100, choices=COUNTRY_CHOICES, verbose_name="Страна")
    def __str__(self):
        return f"{self.mark_names} {self.model} ({self.year}) - {self.price} ₽"

class TelegramAdImage(models.Model):
    ad = models.ForeignKey(TelegramAd, on_delete=models.CASCADE, related_name="images")
    image = models.TextField()
    # thumbnail = ImageSpecField(source='image',
    #                            processors=[ResizeToFill(400, 400)],
    #                            format='JPEG',
    #                            options={'quality': 80})
    # def save(self, *args, **kwargs):
    #         # Сначала сохраняем оригинал (если нужно)
    #         super().save(*args, **kwargs)
    #
    #         # Обрабатываем только если есть изображение
    #         if self.image:
    #             self.optimize_image()
    #
    # def optimize_image(self):
    #     img = Image.open(self.image)
    #
    #     # Конвертируем в RGB (если это PNG с прозрачностью)
    #     if img.mode in ('RGBA', 'P'):
    #         img = img.convert('RGB')
    #
    #     # Определяем целевые размеры
    #     max_size = 1200  # Максимальный размер по большей стороне
    #     if max(img.width, img.height) > max_size:
    #         ratio = max_size / max(img.width, img.height)
    #         new_width = int(img.width * ratio)
    #         new_height = int(img.height * ratio)
    #         img = img.resize((new_width, new_height), Image.LANCZOS)
    #
    #     # Сохраняем оптимизированное изображение
    #     temp_file = BytesIO()
    #     img.save(temp_file, format='WEBP', quality=75)  # Или 'JPEG'
    #     temp_file.seek(0)
    #
    #     # Обновляем файл в модели
    #     self.image.save(
    #         f"{self.image.name.split('.')[0]}.webp",
    #         File(temp_file),
    #         save=False
    #     )
    #     super().save(update_fields=['image'])

