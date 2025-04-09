from django.contrib import admin
from django.utils.html import format_html
from .models import TelegramAd, TelegramAdImage


class TelegramAdImageInline(admin.TabularInline):
    """Отображение изображений в карточке объявления"""
    model = TelegramAdImage
    extra = 0  # Не добавляем пустые поля
    readonly_fields = ["display_image"]  # Поле для предпросмотра фото

    def display_image(self, obj):
        """Функция для отображения превью изображений в админке"""
        if obj.image_url:
            return format_html(f'<img src="{obj.image}" style="max-height:100px; max-width:150px; border-radius:5px;" />')
        return "Нет изображения"

    display_image.short_description = "Фото"


@admin.register(TelegramAd)
class TelegramAdAdmin(admin.ModelAdmin):
    list_display = ("id", "mark_names", "model", "year", "mileage", "price", "contact_number", "date_posted", "preview_image")
    list_filter = ("mark_names", "year", "date_posted")
    search_fields = ("mark_names", "model", "contact_number")
    ordering = ("-date_posted",)
    inlines = [TelegramAdImageInline]  # Показываем фото внутри объявления

    def preview_image(self, obj):
        """Отображает главное фото объявления (первое изображение)"""
        first_image = obj.images.first()
        if first_image:
            return format_html(f'<img src="{first_image.image}" style="max-height:50px; max-width:80px; border-radius:5px;" />')
        return "Нет фото"

    preview_image.short_description = "Главное фото"
