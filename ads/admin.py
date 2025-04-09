from django.contrib import admin
from django.utils.html import format_html
from .models import  Ad, AdImage
from django.db import models
from django import forms

class AdImageInline(admin.TabularInline):  # или admin.StackedInline
    model = AdImage
    extra = 1  # Количество пустых полей для загрузки новых изображений
    readonly_fields = ["preview"]  # Добавляем предпросмотр

    def preview(self, obj):
        """Функция для предпросмотра изображений в админке"""
        if obj.image:
            return format_html(f'<img src="{obj.image.url}" style="max-height:100px; max-width:150px;" />')
        return "Нет изображения"

@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ("mark_names", "model", "price", "status", "owner", "created_at", "preview_image")  # Поля, отображаемые в списке
    list_filter = ("status", "mark_names", "model")  # Фильтры по статусу, марке и модели
    search_fields = ("mark_names", "model", "description")  # Поиск по названию, марке, модели и описанию
    ordering = ("-created_at",)  # Сортировка по дате создания (от новых к старым)
    inlines = [AdImageInline]  # Добавляем изображения как Inline

    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 2,'cols': 40,'style': 'width: fit-content;  height: auto;'})},
    }

    def preview_image(self, obj):
        """Функция для предпросмотра главного изображения объявления"""
        first_image = obj.images.first()  # Получаем первое изображение
        if first_image:
            return format_html(f'<img src="{first_image.image.url}" style="max-height:50px; max-width:80px;" />')
        return "Нет фото"

    preview_image.short_description = "Фото"