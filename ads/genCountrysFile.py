import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # замени на свой путь
django.setup()

from ads.models import CarsDataTest

# Получим уникальные страны, уберем пустые
unique_countries = (
    CarsDataTest.objects.exclude(country__isnull=True)
    .exclude(country__exact="")
    .values_list("country", flat=True)
    .distinct()
)

# Преобразуем в список кортежей для choices
country_choices = sorted(set((c, c) for c in unique_countries))
# for choice in country_choices:
#     print(choice)

output_file = os.path.join(os.path.dirname(__file__), "country_choices.py")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("# Автоматически сгенерировано из CarsDataTest\n")
    f.write("COUNTRY_CHOICES = [\n")
    for c in country_choices:
        f.write(f"    ({repr(c[0])}, {repr(c[1])}),\n")
    f.write("]\n")

print(f"\n✔️ Файл успешно сохранён как: {output_file}")


