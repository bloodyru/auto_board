import re
import phonenumbers
from ads.models import CarsDataTest
from asgiref.sync import sync_to_async  # Импортируем sync_to_async

from django.core.cache import cache


CAR_BRANDS = list(CarsDataTest.objects.values_list("mark_name", flat=True).distinct().order_by("mark_name"))

# Словарь для сопоставления альтернативных названий брендов
BRAND_ALIASES = {
    "Lada (ВАЗ)": ["Lada", "ВАЗ", "калину", "калина"],
    "Mercedes-Benz": ["Mercedes", "Mercedes-Benz"],
    "Volkswagen": ["VW", "Volkswagen"],
    "Chevrolet": ["Шевроле"],
    "Mazda": ["Мазда"],
    "Renault": ["Рено"],
}

async def extract_car_info(message):
    """Функция извлекает марку, модель, год выпуска, пробег, цену и телефон из текста"""
    if not message.message:
        print(f"Нет текста прерываю обработку {message.id}-{message.message}")
        return None, None, None, None, None, None

    brand, model, year, mileage, price, contact_number = None, None, None, None, None, None

    # Перебираем все бренды, включая альтернативные названия
    for car_brand in CAR_BRANDS:
        brand_variants = [car_brand] + BRAND_ALIASES.get(car_brand, [])
        for variant in brand_variants:
            if re.search(rf"\b{re.escape(variant)}\b", message.message, re.IGNORECASE):
                brand = car_brand
                break
        if brand:
            models = await get_cached_models(brand)  # Просто вызываем await
            for one_model in models:
                if re.search(rf"\b{re.escape(one_model)}\b", message.message, re.IGNORECASE):
                    model = one_model
                    break

    # if message.photo:
    #     await get_media_from_message(message)

    # if not brand or not model and message.photo:
    #     print(f"ЕСТЬ ФОТО и есть текст но не найдены марка и модель в тексте:\n {message.message}")
    #     return None, None, None, None, None, None

    # Поиск года
    year_match = re.search(r"\b(19\d{2}|20[0-3]\d)\b", message.message)
    if year_match:
        year = int(year_match.group(1))

    # Поиск пробега
    mileage_match = re.search(r"(\d{1,6})\s?(км|к)\b", message.message, re.IGNORECASE)
    if mileage_match:
        mileage = int(mileage_match.group(1))

    # Поиск цены
    price = extract_price(message.message)

    # Поиск телефона
    for match in re.finditer(r"\+?\d{10,15}", message.message):
        phone = phonenumbers.parse(match.group(), "RU")
        if phonenumbers.is_valid_number(phone):
            contact_number = phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            break
    return brand, model, year, mileage, price, contact_number

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