from rest_framework import viewsets, permissions

# from telegramm_parse.forms import TelegramAdForm
from telegramm_parse.models import TelegramAd
from .models import Ad
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Ad, Profile, CarsDataTest, AdImage
from .forms import AdForm, ProfileForm, RegisterForm
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib import messages
from django.core.exceptions import ValidationError
from PIL import Image
from functools import lru_cache


def validate_image_file(image_field):
    try:
        img = Image.open(image_field)
        img.verify()  # Проверяет, что файл читается как изображение
    except Exception:
        raise ValidationError(f"Файл {image_field.name} не является корректным изображением.")

@lru_cache(maxsize=None)
def get_car_marks():
    return list(CarsDataTest.objects.values("mark_name").distinct().order_by("mark_name"))

def home(request):
    # Получаем все имеющиеся марки
    marks = get_car_marks()
    # marks = CarsDataTest.objects.values("mark_name").distinct().order_by("mark_name")
    combined_ads = ad_list(request)
    from ads.models import Ad
    from .country_choices import COUNTRY_CHOICES
    COLOR_CHOICES = Ad.COLOR_CHOICES
    return render(request, "ads/home.html", {"combined_ads": combined_ads, "marks": marks, "COLOR_CHOICES":COLOR_CHOICES, "COUNTRY_CHOICES":COUNTRY_CHOICES})



def ad_list(request):
    brand = request.GET.get("brand", "").strip()
    model = request.GET.get("model", "").strip()
    price_low = request.GET.get("price_low", "").strip()
    price_max = request.GET.get("price_max", "").strip()
    year_low = request.GET.get("year_low", "").strip()
    year_max = request.GET.get("year_max", "").strip()
    fuel_type = request.GET.get("fuel_type", "").strip()
    gearbox = request.GET.get("gearbox", "").strip()
    body_type = request.GET.get("body_type", "").strip()
    exchange = request.GET.get("exchange", "").strip()
    seller = request.GET.get("seller", "").strip()
    drive = request.GET.get("drive", "").strip()
    mileage_low = request.GET.get("mileage_low", "").strip()
    mileage_max = request.GET.get("mileage_max", "").strip()
    location = request.GET.get("location", "").strip()
    damaged = request.GET.get("damaged", "").strip()
    steering = request.GET.get("steering", "").strip()
    color = request.GET.get("color", "").strip()
    documents = request.GET.get("documents", "").strip()
    country = request.GET.get("country", "").strip()
    query = Q()  # Создаем пустой Q-объект
    if brand:
        query &= Q(mark_names__icontains=brand)  # Добавляем условие
    if model:
        query &= Q(model__icontains=model)  # Добавляем условие
    if price_max:
        try:
            price_max = float(price_max)
            query &= Q(price__lte=price_max)  # Добавляем условие
            print(query)
        except ValueError:
            pass  # Если ошибка, просто игнорируем
    if price_low:
        try:
            price_low = float(price_low)
            query &= Q(price__gte=price_low)  # Добавляем условие
            print(query)
        except ValueError:
            pass  # Если ошибка, просто игнорируем
    if year_low:
        try:
            year_low = float(year_low)
            query &= Q(year__gte=year_low)  # Добавляем условие
            print(query)
        except ValueError:
            pass  # Если ошибка, просто игнорируем
    if year_max:
        try:
            year_max = float(year_max)
            query &= Q(year__lte=year_max)  # Добавляем условие
            print(query)
        except ValueError:
            pass  # Если ошибка, просто игнорируем
    if fuel_type:
        query &= Q(fuel_type=fuel_type)
    if gearbox:
        query &= Q(gearbox__icontains=gearbox)  # КПП
    if body_type:
        query &= Q(body_type__icontains=body_type)  # Кузов
    if exchange:
        query &= Q(exchange=True)  # Обмен
    if seller:
        query &= Q(seller__icontains=seller)  # Продавец
    if drive:
        query &= Q(drive__icontains=drive)  # Привод
    if mileage_max:
        try:
            mileage_max = float(mileage_max)
            query &= Q(mileage__lte=mileage_max)  # Добавляем условие
            print(query)
        except ValueError:
            pass  # Если ошибка, просто игнорируем
    if mileage_low:
        try:
            mileage_low = float(mileage_low)
            query &= Q(mileage__gte=mileage_low)  # Добавляем условие
            print(query)
        except ValueError:
            pass  # Если ошибка, просто игнорируем
    if location:
        query &= Q(location__icontains=location)  # Состояние(вналичии или под заказ)
    if damaged:
        query &= Q(damaged__icontains=damaged)  # Состояние
    if steering:
        query &= Q(steering__icontains=steering)  # Состояние
    if color:
        query &= Q(color__icontains=color)  # Состояние
    if documents:
        query &= Q(documents__icontains=documents)  # Состояние
    if country:
        query &= Q(country__icontains=country)  # Состояние

    ads = Ad.objects.filter(query).prefetch_related("images").order_by("-created_at")
    adsTelegramm = TelegramAd.objects.filter(query).prefetch_related("images").order_by("-date_posted")
    combined_ads = sorted(list(ads) + list(adsTelegramm), key=lambda ad: ad.created_at, reverse=True)
    print(f"Найдено объявлений: {ads.count()} {query}")
    return combined_ads

def ad_detail(request, source, ad_id):
    if source == "telegram":
        ad = get_object_or_404(TelegramAd.objects.prefetch_related("images"), id=ad_id)
    elif source == "web":
        ad = get_object_or_404(Ad.objects.prefetch_related("images"), id=ad_id)
    return render(request, "ads/ad_detail.html", {"ad": ad})

@login_required
def ad_create(request):
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_IMAGE_COUNT = 10  # Максимальное число изображений

    if request.method == "POST":
        form = AdForm(request.POST, request.FILES)
        images = request.FILES.getlist("images")
        print("111111111111111111111111111111111",images)
        if form.is_valid():
            # Сначала создаем объявление
            ad = form.save(commit=False)
            ad.owner = request.user
            ad.status = "active"
            ad.save()  # Теперь у нас есть `ad.id`

            valid_images = []
            for image in images:
                try:
                    # Валидация
                    validate_image_file(image)
                    # Создаем и сохраняем AdImage
                    ad_image = AdImage(ad=ad, image=image)
                    ad_image.full_clean()  # Проверка модели
                    ad_image.save()
                    valid_images.append(ad_image)
                except ValidationError as e:
                    messages.error(request, f"Ошибка в файле {image.name}: {e}")

            # Если есть ошибки в изображениях, удаляем объявление
            if len(valid_images) != len(images):
                print("len(valid_images) != len(images)")
                ad.delete()  # Удаляем объявление, так как не все изображения корректны
                return render(request, "ads/ad_form.html", {"form": form})

            #  Сохраняем валидные изображения
            for ad_image in valid_images:
                ad_image.save()

            messages.success(request, "Объявление успешно создано!")
            return redirect("profile")
        else:
            messages.error(request, "Ошибка при создании объявления.")
            return render(request, "ads/ad_form.html", {"form": form})
    else:
        form = AdForm()

    return render(request, "ads/ad_form.html", {"form": form})


def get_model_specs(request):
    mark = request.GET.get('mark')  # "Alfa%20Romeo"
    model = request.GET.get('model')
    queryset = CarsDataTest.objects.filter(mark_name=mark,model_name=model)

    # Получаем уникальные значения из базы
    engine_types = list(queryset
                        .values_list('engine_type', flat=True).distinct()
                        .exclude(engine_type__isnull=True)
                        .exclude(engine_type__exact='')
                        )
    body_type = list(queryset
                        .values_list('body_type', flat=True).distinct()
                        .exclude(engine_type__isnull=True)
                        .exclude(engine_type__exact='')
                        )
    transmission = list(queryset
                        .values_list('transmission', flat=True).distinct()
                        .exclude(engine_type__isnull=True)
                        .exclude(engine_type__exact='')
                        )
    FUEL_TYPE_MAPPING = {
        'бензин': 'petrol',
        'дизель': 'diesel',
        'СУГ': 'gas',
        'электро': 'electric',
        'гибрид': 'hybrid',
        'гидроген': 'gas'  # преобразуем гидроген в gas (или другое значение по вашему выбору)
    }
    # Преобразуем значения через словарь
    mapped_engine_types = [FUEL_TYPE_MAPPING.get(engine, engine) for engine in engine_types if
                           engine in FUEL_TYPE_MAPPING]

    # Удаляем дубликаты после преобразования
    unique_engine_types = list(set(mapped_engine_types))
    return JsonResponse ({'engine_type': unique_engine_types,'body_type': body_type,
                          'transmission': transmission,})

@login_required
def profile_view(request):
    profile = Profile.objects.select_related('user').get_or_create(user=request.user)[0]
    user_ads = Ad.objects.filter(owner=request.user).order_by("-created_at")

    if request.method == 'POST':
        # Обработка данных из модального окна
        username = request.POST.get('username')
        contact_number = request.POST.get('contact_number')

        # Обновляем данные пользователя
        if username and username != request.user.username:
            request.user.username = username
            request.user.save()

        # Обновляем профиль
        if contact_number != profile.contact_number:
            profile.contact_number = contact_number
            profile.save()

        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('profile')

    context = {
        'profile': profile,
        'user_ads': user_ads
    }
    return render(request, 'ads/profile.html', context)

@login_required
def ad_edit(request, ad_id, source):
    ad = get_object_or_404(Ad, id=ad_id, owner=request.user)  # Только владелец может редактировать
    if request.method == 'POST':
        form = AdForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            # Обработка дополнительных загруженных изображений:
            images = request.FILES.getlist("images")
            valid_images = []
            for image in images:
                try:
                    ad_image = AdImage(ad=ad, image=image)
                    ad_image.full_clean()
                    valid_images.append(ad_image)
                except ValidationError as e:
                    messages.error(request, f"Ошибка в файле {image.name}: {e}")
            for ad_image in valid_images:
                ad_image.save()

            return redirect('profile')  # После редактирования возвращаемся в профиль
    else:
        form = AdForm(instance=ad)

    return render(request, 'ads/ad_edit.html', {'form': form, 'ad': ad, 'edit_mode': True})


@login_required
def ad_delete(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id, owner=request.user)
    if request.method == "POST":
        ad.delete()
        messages.success(request, "Объявление успешно удалено.")
        return redirect("profile")
    # Если метод не POST, можно отобразить подтверждение удаления
    return render(request, "ads/ad_confirm_delete.html", {"ad": ad})



class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    # serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

def logout_view(request):
    if request.method == "POST":  # Django требует POST-запрос для logout
        logout(request)
        return redirect("home")  # Перенаправляем пользователя на главную страницу
    return redirect("home")  # Если кто-то попытается зайти на /logout/ напрямую


def search_ads(request):
    query = request.GET.get("q", "")
    ads = Ad.objects.filter(title__icontains=query) if query else Ad.objects.all()
    car_data = AdData.objects.filter(mark_name__icontains=query) if query else AdData.objects.all()
    return render(request, "ads/search_results.html", {"ads": ads, "car_data": car_data, "query": query})

def get_models(request):
    brand_name = request.GET.get("brand")
    if brand_name:
        models = CarsDataTest.objects.filter(mark_name=brand_name).values_list("model_name", flat=True).distinct()
    else:
        models = []

    return JsonResponse({"models": list(models)}, safe=False)

def get_generations(request):
    mark = request.GET.get("mark", "").strip()
    model = request.GET.get("model", "").strip()
    print("Получен запрос на поколения:", mark, model)

    generations = []

    if mark and model:
        generations = CarsDataTest.objects.filter(
            mark_name=mark,
            model_name=model
        ).exclude(
            generation_name__isnull=True
        ).exclude(
            generation_name__exact=""
        ).exclude(
            generation_name__regex=r'^\s*$'  # Убираем строки из одних пробелов
        ).values_list("generation_name", flat=True).distinct()

    return JsonResponse({"generations": list(generations)}, safe=False)



def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password1"])
            user.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect("home")  # Перенаправляем на главную страницу
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})

def get_brands(request):
    term = request.GET.get("term", "").strip()
    brands = (
        CarsDataTest.objects.filter(mark_name__icontains=term)
        .values_list("mark_name", flat=True)
        .distinct()[:10]  # Ограничиваем 10 результатами
    )
    return JsonResponse({"brands": list(brands)})

def delete_image(request, image_id):
    if request.method == "DELETE":
        image = get_object_or_404(AdImage, id=image_id)
        if request.user == image.ad.owner:  # Проверяем владельца объявления
            image.delete()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Нет доступа"}, status=403)
    return JsonResponse({"success": False, "error": "Неверный запрос"}, status=400)