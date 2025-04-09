from telegramm_parse.models import TelegramAd


ads = TelegramAd.objects.all()
for ad in ads:
    print(f"ID: {ad.message_id}, Марка: {ad.brand}, Модель: {ad.model}, Год: {ad.year}, Пробег: {ad.mileage}, Телефон: {ad.contact_number}")
