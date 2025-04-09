from django.conf import settings  # Импортируем настройки Django
import os
import asyncio



# Определяем путь к глобальной папке медиафайлов
IMAGES_DIR = os.path.join(settings.MEDIA_ROOT, "telegram_ads")
os.makedirs(IMAGES_DIR, exist_ok=True)  # Создаём папку, если её нет

async def get_media_from_message(group, client, brand):
    """Асинхронно загружает фото, избегая дубликатов."""
    photo_paths = set()
    for msg in group:
        """Функция скачивания фото."""
        if msg.photo:
            photo_filename = f"{brand}_{msg.id}_{msg.photo.id}.jpg"
            relative_path = f"{settings.MEDIA_URL}telegram_ads/{photo_filename}"  # Относительный путь для БД
            absolute_path = os.path.join(IMAGES_DIR, photo_filename)  # Абсолютный путь

            if not os.path.exists(absolute_path):  # Проверяем, скачивалось ли фото
                try:
                    await client.download_media(message=msg, file=absolute_path)
                    # await msg.download(file_name=absolute_path)
                    photo_paths.add(relative_path)
                    print(f"📸 Фото скачано: {absolute_path}")
                except Exception as e:
                    print(f"❌ Ошибка скачивания {photo_filename}: {e}")
                    return None  # Не добавляем ошибочные фото

    return photo_paths  # Возвращаем путь для сохранения в БД


