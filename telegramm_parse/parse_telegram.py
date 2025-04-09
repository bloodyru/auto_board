import asyncio

from pyrogram import Client
from pyrogram.types import Message
import os
import sys
import django
import re
from django.conf import settings  # Импортируем настройки Django

import phonenumbers
from asgiref.sync import sync_to_async  # Импортируем sync_to_async

# Указываем путь к Django-проекту
sys.path.append("/home/t/PycharmProjects/auto_board")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from ads.models import CarsDataTest
from telegramm_parse.models import TelegramAd, TelegramAdImage  # Импортируем модель

# Данные для авторизации в Telegram API
CHANNEL = "AvtoprodagaVolnovahairayon"  # Имя канала или его ID
# CHANNEL = "LNR_AVTO"  # Имя канала или его ID


# Подключение к Telegram API как пользователь
app = Client(
    "session_name",
    api_id=24035219,
    api_hash="0ebf5b6846f7e4782ec98ea0e5c4a246"
)

from django.core.cache import cache
from ads.models import CarsDataTest


def get_cached_brands():
    """Получаем кэшированные марки авто"""
    brands = cache.get("car_brands")

    if not brands:  # Если кэша нет, загружаем из БД
        brands = list(CarsDataTest.objects.values_list("mark_name", flat=True).distinct())
        cache.set("car_brands", brands, timeout=60 * 60 * 24)  # Кэшируем на 24 часа
        print("🔄 Кэш марок обновлен")

    return brands

@sync_to_async
def get_cached_models(brand):
    """Получаем кэшированные модели авто по марке"""
    cache_key = f"car_models_{brand}"
    models = cache.get(cache_key)

    if not models:  # Если нет в кэше, загружаем из БД
        models = list(CarsDataTest.objects.filter(mark_name=brand).values_list("model_name", flat=True).distinct())
        cache.set(cache_key, models, timeout=60 * 60 * 24)  # Кэшируем на 24 часа
        print(f"🔄 Кэш моделей для {brand} обновлен")

    return models


# Определяем путь к глобальной папке медиафайлов
IMAGES_DIR = os.path.join(settings.MEDIA_ROOT, "telegram_ads")
os.makedirs(IMAGES_DIR, exist_ok=True)  # Создаём папку, если её нет

# Список марок автомобилей
CAR_BRANDS = list(CarsDataTest.objects.values_list("mark_name", flat=True).distinct().order_by("mark_name"))
CAR_BRANDS = get_cached_brands()

@sync_to_async
def get_car_models(brand):
    """Функция выполняет SQL-запрос в синхронном режиме."""
    return list(CarsDataTest.objects.filter(mark_name=brand).values_list("model_name", flat=True).distinct())

# Словарь для сопоставления альтернативных названий брендов
BRAND_ALIASES = {
    "Lada (ВАЗ)": ["Lada", "ВАЗ"],
    "Mercedes-Benz": ["Mercedes", "Mercedes-Benz"],
    "Volkswagen": ["VW", "Volkswagen"],
}

async def extract_car_info(text):
    """Функция извлекает марку, модель, год выпуска, пробег, цену и телефон из текста"""
    # if not text:
    #     print("Сообщение не содержит текста")
    #     return None, None, None, None, None, None

    brand, model, year, mileage, price, contact_number = None, None, None, None, None, None

    # Перебираем все бренды, включая альтернативные названия
    for car_brand in CAR_BRANDS:
        brand_variants = [car_brand] + BRAND_ALIASES.get(car_brand, [])
        for variant in brand_variants:
            if re.search(rf"\b{re.escape(variant)}\b", text, re.IGNORECASE):
                brand = car_brand
                break
        if brand:
            break

    if brand:
        models = await get_cached_models(brand)  # Просто вызываем await
        for one_model in models:
            if re.search(rf"\b{re.escape(one_model)}\b", text, re.IGNORECASE):
                model = one_model
                break

    if not brand or not model:
        print(f"Не найдены марка и модель в тексте: {text}")
        return None, None, None, None, None, None

    # Поиск года
    year_match = re.search(r"\b(19\d{2}|20[0-3]\d)\b", text)
    if year_match:
        year = int(year_match.group(1))

    # Поиск пробега
    mileage_match = re.search(r"(\d{1,6})\s?(км|к)\b", text, re.IGNORECASE)
    if mileage_match:
        mileage = int(mileage_match.group(1))

    # Поиск цены
    price = extract_price(text)

    # Поиск телефона
    for match in re.finditer(r"\+?\d{10,15}", text):
        phone = phonenumbers.parse(match.group(), "RU")
        if phonenumbers.is_valid_number(phone):
            contact_number = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            break

    return brand, model, year, mileage, price, contact_number

@sync_to_async
def ad_exists(message_id):
    """Асинхронная проверка существования объявления в базе"""
    return TelegramAd.objects.filter(message_id=message_id).exists()

@sync_to_async
def save_ad(message, photo_paths, brand, model, year, mileage, price, contact_number):
    """Сохранение объявления в БД"""
    try:
        text = message.text or message.caption or "Текст отсутствует"  # ✅ Добавляем fallback
        ad = TelegramAd.objects.create(
            message_id=message.id,
            text=text,  # ✅ Гарантируем, что текст не пустой
            date_posted=message.date,
            brand=brand,
            model=model,
            year=year,
            mileage=mileage,
            price=price,
            contact_number=contact_number
        )
        for photo in photo_paths:
            TelegramAdImage.objects.create(ad=ad, image_url=photo)
        print(f"✅ Объявление {message.id} сохранено в БД.")
    except Exception as e:
        print(f"❌ Ошибка при сохранении объявления {message.id}: {e}")


async def get_media_from_message(message):
    """Асинхронно загружает фото, избегая дубликатов."""
    photo_paths = set()

    async def download_photo(msg):
        """Функция скачивания фото."""
        if msg.photo:
            photo_filename = f"{msg.id}_{msg.photo.file_unique_id}.jpg"
            relative_path = f"{settings.MEDIA_URL}telegram_ads/{photo_filename}"  # Относительный путь для БД
            absolute_path = os.path.join(IMAGES_DIR, photo_filename)  # Абсолютный путь

            if not os.path.exists(absolute_path):  # Проверяем, скачивалось ли фото
                try:
                    await msg.download(file_name=absolute_path)
                    print(f"📸 Фото скачано: {relative_path}")
                except Exception as e:
                    print(f"❌ Ошибка скачивания {photo_filename}: {e}")
                    return None  # Не добавляем ошибочные фото

            return relative_path  # Возвращаем путь для сохранения в БД

    tasks = []
    if message.media_group_id:
        media_group = await app.get_media_group(message.chat.id, message.id)
        tasks = [download_photo(m) for m in media_group]
    else:
        tasks.append(download_photo(message))

    results = await asyncio.gather(*tasks)  # Асинхронно скачиваем фото
    return [r for r in results if r]  # Убираем `None`


from pyrogram.errors import FloodWait
import random


async def parse_channel():
    """Парсим Telegram-канал с защитой от FloodWait."""
    async with app:
        print(f"🔎 Читаем последние 10 сообщений из канала {CHANNEL}...")

        messages = []

        # while True:
        try:
            async for message in app.get_chat_history(CHANNEL, limit=1):
                messages.append(message)
                print(f"📩 Сообщение {message.id} получено")
                await asyncio.sleep(random.uniform(1, 4))  # 🕒 Случайная задержка

            if not messages:
                print("⚠️ В чате нет новых сообщений!")

            for msg in messages:
                await process_message(msg)
                await asyncio.sleep(random.uniform(2, 5))  # 🕒 Пауза между обработкой сообщений

            # После обработки ждем перед следующим запросом
            await asyncio.sleep(random.uniform(10, 30))  # ⏳ Ожидание перед следующим циклом

        except FloodWait as e:
            print(f"⏳ Telegram API заблокировал запросы! Ждем {e.value} секунд...")
            await asyncio.sleep(e.value)  # Ждем время, которое требует Telegram

async def process_message(message):
    """Обрабатывает каждое сообщение в отдельной задаче."""

    # 1️⃣ Проверяем, если сообщение относится к медиа-группе
    if message.media_group_id:
        media_group = await app.get_media_group(message.chat.id, message.id)
        for msg in media_group:
            await process_message(msg)  # Обрабатываем каждое фото в группе
        return  # Уже обработали, выходим

    # 2️⃣ Пропускаем сообщения без текста и подписи
    if not message.text and not message.caption:
        print(f"⏩ Пропущено сообщение {message.id} (нет текста) - {message}")
        return

    # 3️⃣ Проверяем, существует ли объявление в базе
    if await ad_exists(message.id):
        print(f"⏩ Пропущено объявление {message.id} (уже существует)")
        return

    print(f"🔹 Обрабатывается сообщение {message.id}")

    # 4️⃣ Извлекаем данные об авто из текста
    brand, model, year, mileage, price, contact_number = await extract_car_info(
        message.text or message.caption
    )

    # 5️⃣ Если не удалось определить марку и модель — пропускаем
    if not brand or not model:
        print(f"⏩ Пропущено объявление {message.id} (не найдены марка и модель)")
        return

    # 6️⃣ Если всё в порядке, сохраняем объявление
    await process_ad(message, brand, model, year, mileage, price, contact_number)


from django.utils.timezone import make_aware

async def process_ad(message, brand, model, year, mileage, price, contact_number):
    """Сохраняет объявление и фото в базу данных."""
    try:
        photo_paths = await get_media_from_message(message)  # 🔹 Загружаем фото

        # 🔹 Делаем `date_posted` timezone-aware
        date_posted = make_aware(message.date) if message.date.tzinfo is None else message.date

        ad = await sync_to_async(TelegramAd.objects.create)(
            message_id=message.id,
            text=message.text or message.caption,
            date_posted=date_posted,
            brand=brand,
            model=model,
            year=year,
            mileage=mileage,
            price=price,
            contact_number=contact_number,
        )

        # 🔹 Асинхронно сохраняем фото
        image_tasks = [
            sync_to_async(TelegramAdImage.objects.create)(ad=ad, image_url=photo)
            for photo in photo_paths
        ]
        await asyncio.gather(*image_tasks)

        print(f"✅ Сохранено объявление {message.id}: {brand} {model}, {year}, {price} руб., {mileage} км, {contact_number} (Фото: {photo_paths})")
    except Exception as e:
        print(f"❌ Ошибка при сохранении объявления {message.id}: {e}")


def extract_price(text):
    """Извлекает цену из текста."""
    price_match = re.search(
        r"\b(\d{1,3}(?:[.,\s]?\d{3})*|\d+(\.\d+)?)\s*(млн|кк|тыс|т\.р|тыс\.руб|к)?",
        text, re.IGNORECASE
    )

    if price_match:
        price_str = price_match.group(1).replace(",", "").replace(".", "").replace("\xa0", "").replace(" ", "")

        try:
            price = int(price_str)
        except ValueError:
            print(f"⚠️ Ошибка при обработке цены: {price_str}")
            return None  # Возвращаем `None`, если ошибка

        multiplier = price_match.group(3)

        if multiplier:
            if "млн" in multiplier or "кк" in multiplier:
                price *= 1_000_000
            elif "тыс" in multiplier or "т.р" in multiplier:
                price *= 1_000

        if price > 2_147_483_647:
            price = 999_999_999  # Предельное значение

        return price

    return None


# Запуск
app.run(parse_channel())