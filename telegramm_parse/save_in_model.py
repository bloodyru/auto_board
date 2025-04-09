import asyncio
from asgiref.sync import sync_to_async
from django.utils.timezone import make_aware

from telegramm_parse.models import TelegramAd, TelegramAdImage

async def save_ad(one_mess_from_group_messaged, brand, model, year, mileage, price, contact_number, photo_path, channel):
    """Сохраняет объявление и фото в базу данных."""
    message = one_mess_from_group_messaged
    link = f"https://t.me/{channel}/{message.id}"

    try:
        # 🔹 Делаем `date_posted` timezone-aware
        date_posted = make_aware(message.date) if message.date.tzinfo is None else message.date

        ad = await sync_to_async(TelegramAd.objects.create)(
            message_id=message.id,
            description=message.text or message.caption,
            date_posted=date_posted,
            mark_names=brand,
            model=model or "",
            year=year or 1900,
            mileage=mileage  or 0,
            price=price or 0,
            contact_number=contact_number  or "",
            link = link  or "",
        )

        # 🔹 Асинхронно сохраняем фото
        image_tasks = [sync_to_async(TelegramAdImage.objects.create)(ad=ad, image=photo)
            for photo in photo_path]
        await asyncio.gather(*image_tasks)

        print(f"✅ Сохранено объявление {message.id}: {brand} {model}, {year}, {price} руб., {mileage} км, {contact_number} (Фото: {photo_path})")
    except Exception as e:
        print(f"❌ Ошибка при сохранении объявления {message.id}: {e}")
