import asyncio
import os
import sys
import django
# Указываем путь к Django-проекту
sys.path.append("/home/t/PycharmProjects/auto_board")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from telethon import TelegramClient
from telethon import errors
from collections import defaultdict
from car_info import extract_car_info
import re
from get_photo import get_media_from_message
from save_in_model import save_ad


from django.core.cache import cache
import phonenumbers

# Указываем путь к Django-проекту и устанавливаем переменную окружения
sys.path.append("/home/t/PycharmProjects/auto_board")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()  # Важно: инициализируем Django до использования моделей


from config import settings

# Данные, полученные на my.telegram.org
api_id = 24035219
api_hash = '0ebf5b6846f7e4782ec98ea0e5c4a246'
client = TelegramClient('anon', api_id, api_hash)
channel = 'AvtoprodagaVolnovahairayon'  # ID или username канала
# channel = 'LNR_AVTO'  # ID или username канала


# Определяем путь к глобальной папке медиафайлов
IMAGES_DIR = os.path.join(settings.MEDIA_ROOT, "telegram_ads")
os.makedirs(IMAGES_DIR, exist_ok=True)  # Создаём папку, если её нет

# Лимит сообщений:
limit = 100
semaphore = asyncio.Semaphore(5)

"""ОСНОВНОЙ ЦИКЛ"""
async def main():
    async with semaphore:
        try:
            await client.start()
            grouped_messages = defaultdict(list)
            not_grouped_messages = defaultdict(list)

            """Формируем словари с групповыми и одиночными сообщениями"""
            async for message in client.iter_messages(channel, limit):
                if message.grouped_id:
                    grouped_messages[message.grouped_id].append(message)
                else:
                    # link = f"https://t.me/{channel}/{message.id}"
                    not_grouped_messages[message.id].append(message)

            """Итерация групповых сообщений"""

            for one_group in grouped_messages:
                group = grouped_messages[one_group]

                for one_mess_from_group_messaged in group:
                    if one_mess_from_group_messaged.message:
                        brand, model, year, mileage, price, contact_number = await extract_car_info(one_mess_from_group_messaged)
                        if brand != None:
                            print("MAINMAINMAINMAINMAINMAINMAINMAINMAIN \n", brand, model, year, mileage, price, contact_number)
                            photo_path = await get_media_from_message (group, client, brand)
                            print(photo_path)
                            await save_ad(one_mess_from_group_messaged, brand, model, year, mileage, price, contact_number, photo_path, channel)

                        else:
                            print("!!!!!!!!!!!!!!!!!!!!!!!!!!\n", brand, model, year, mileage, price, contact_number)
                            print(one_mess_from_group_messaged.message)


            """Итерация одиночных сообщений"""
            for mess in not_grouped_messages:
                ONEMESS = not_grouped_messages[mess]
                for one_mess in ONEMESS:
                    if one_mess.message:
                        pass
                        # print(one_mess.message)
                    if one_mess.photo:
                        pass
                        # print(one_mess.photo)
        except errors.FloodWaitError as e:
            print(f"FloodWait: Ждем {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
if __name__ == "__main__":
    asyncio.run(main())