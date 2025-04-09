import os

from django.db import models
from django.contrib.auth import get_user_model

from django.core.exceptions import ValidationError
from PIL import Image
from django.core.files import File
from io import BytesIO
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.contrib.postgres.aggregates import ArrayAgg

from .country_choices import COUNTRY_CHOICES

User = get_user_model()

def validate_image(image):
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = ["jpeg", "jpg", "png", "gif", "webp"]
    MIN_WIDTH, MIN_HEIGHT = 300, 300

    # Проверяем размер файла
    if image.size > MAX_UPLOAD_SIZE:
        raise ValidationError(f"Размер файла {image.name} превышает 5MB.")

    # Проверяем расширение файла
    ext = image.name.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Файл {image.name} имеет недопустимое расширение ({ext}).")

    # Проверяем размеры изображения
    try:
        img = Image.open(image)
        width, height = img.size
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            raise ValidationError(f"Минимальный размер изображения: {MIN_WIDTH}x{MIN_HEIGHT}px. Загружено: {width}x{height}px.")
    except Exception:
        raise ValidationError(f"Файл {image.name} не является корректным изображением.")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to=f"profiles/", blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True, default="")

    def __str__(self):
        return self.user.username


class Ad(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("pending", "Pending"),
        ("sold", "Sold"),
    ]
    FUEL_TYPE_CHOICES = [
        ("petrol", "Бензин"),
        ("diesel", "Дизель"),
        ("gas", "Газ"),
        ("electric", "Электро"),
        ("hybrid", "Гибрид"),
    ]

    GEARBOX_TYPE_CHOICES = [
        ("automatic", "Автомат"),
        ("machanical", "Механика"),
    ]

    BODY_TYPE_CHOICES = [
        ("sedan", "Седан"),
        ("hatchback", "Хэтчбек"),
        ("suv", "Внедорожник"),
        ("station_wagon", "Универсал"),
        ("minivan", "Минивэн"),
        ("pickup", "Пикап"),
        ("limousine", "Лимузин"),
        ("van", "Фургон"),
        ("convertible", "Кабриолет"),
    ]

    SELLER_TYPE_CHOICES = [
        ("private", "Частник"),
        ("company", "Компания"),
    ]

    DRIVE_TYPE_CHOICES = [
        ("front", "Передний"),
        ("rear", "Задний"),
        ("4x4", "Полный"),
    ]

    LOCATION_CHOICES = [
        ("in_stock", "В наличии"),
        ("in_transit", "В пути"),
        ("on_order", "Под заказ"),
    ]

    DAMAGED_CHOICES = [
        ("ok", "Целая/На ходу"),
        ("damaged", "Битая/Не на ходу"),
    ]

    STEERING_CHOICES = [
        ("left", "Левый"),
        ("right", "Правый"),
    ]

    COLOR_CHOICES = [
        ("black", "Черный"),
        ("gray", "Серый"),
        ("white", "Белый"),
        ("blue", "Синий"),
        ("red", "Красный"),
        ("green", "Зеленый"),
        ("orange", "Оранжевый"),
        ("yellow", "Желтый"),
    ]

    DOCUMENTS_CHOICES = [
        ("ok", "В порядке"),
        ("bad", "Нет/проблемные"),
    ]


    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ads")
    mark_names = models.TextField()
    model = models.TextField()
    year = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField(verbose_name="Пробег (км)")
    description = models.TextField(verbose_name="Описание")
    # images = models.ManyToManyField("AdImage", blank=True, related_name="ads")  # Связь с изображениями
    # image = models.ImageField(upload_to="ads/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Статус")
    source = models.CharField(max_length=3, default="web", verbose_name="Откуда объвление")
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPE_CHOICES, default="petrol", verbose_name="Топливо")
    gearbox = models.CharField(max_length=10, choices=GEARBOX_TYPE_CHOICES, default="machanical", verbose_name="Коробка")
    body_type = models.CharField(max_length=15, choices=BODY_TYPE_CHOICES, default="sedan", verbose_name="Кузов")
    exchange = models.BooleanField( default=False, verbose_name="Обмен", help_text="Отметьте, если хотите обмен авто")
    seller = models.CharField(max_length=7, choices=SELLER_TYPE_CHOICES, default="private", verbose_name="Продвец")
    drive = models.CharField(max_length=7, choices=DRIVE_TYPE_CHOICES, default="front", verbose_name="Привод")
    location = models.CharField( max_length=10, choices=LOCATION_CHOICES, default="in_stock", blank=True, verbose_name="Статус наличия")
    damaged = models.CharField(max_length=10, choices=DAMAGED_CHOICES, default="ok", verbose_name="Состояние")
    steering = models.CharField( max_length=5, choices=STEERING_CHOICES, default="left", verbose_name="Руль")
    color = models.CharField( max_length=20, choices=COLOR_CHOICES, verbose_name="Цвет", default="white",)
    documents = models.CharField(max_length=20, choices=DOCUMENTS_CHOICES, verbose_name="Документы", default="ok", )
    country = models.CharField( max_length=100, choices=COUNTRY_CHOICES, verbose_name="Страна")

    def __str__(self):
        return f"{self.mark_names} {self.model} ({self.year}) - {self.price}₽"

class AdImage(models.Model):
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="ads", validators=[validate_image])
    thumbnail = ImageSpecField(source='image',
                               processors=[ResizeToFill(400, 400)],
                               format='JPEG',
                               options={'quality': 80})
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        # Сначала сохраняем оригинал (если нужно)
        super().save(*args, **kwargs)

        # Обрабатываем только если есть изображение
        if self.image:
            self.optimize_image()

    def optimize_image(self):
        img = Image.open(self.image)

        # Конвертируем в RGB (если это PNG с прозрачностью)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Определяем целевые размеры
        max_size = 1200  # Максимальный размер по большей стороне
        if max(img.width, img.height) > max_size:
            ratio = max_size / max(img.width, img.height)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)

        # Сохраняем оптимизированное изображение
        temp_file = BytesIO()
        img.save(temp_file, format='WEBP', quality=75)  # Или 'JPEG'
        temp_file.seek(0)

        # Обновляем файл в модели
        self.image.save(
            f"{os.path.splitext(os.path.basename(self.image.name))[0]}.webp",
            File(temp_file),
            save=False
        )
        super().save(update_fields=['image'])

    def __str__(self):
        return f"Image for {self.ad.mark_names} {self.ad.model}"

FUEL_TYPE_MAPPING = {
    'бензин': 'petrol',
    'дизель': 'diesel',
    'СУГ': 'gas',
    'электро': 'electric',
    'гибрид': 'hybrid',
    'гидроген': 'hydrogen'  # Добавьте это значение в FUEL_TYPE_CHOICES если нужно
}

# Обратное преобразование для отображения
FUEL_TYPE_REVERSE_MAPPING = {v: k for k, v in FUEL_TYPE_MAPPING.items()}

class CarsDataTest(models.Model):
    mark_id = models.TextField(blank=True, null=True)
    mark_name = models.TextField(blank=True, null=True)
    mark_cyrillic_name = models.TextField(blank=True, null=True)
    mark_popular = models.TextField(blank=True, null=True)
    country = models.TextField(blank=True, null=True)
    model_id = models.TextField(blank=True, null=True)
    model_name = models.TextField(blank=True, null=True)
    model_cyrillic_name = models.TextField(blank=True, null=True)
    class_field = models.TextField(db_column='class', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    year_from = models.TextField(blank=True, null=True)
    year_to = models.TextField(blank=True, null=True)
    generation_id = models.TextField(blank=True, null=True)
    generation_name = models.TextField(blank=True, null=True)
    year_start = models.TextField(blank=True, null=True)
    year_stop = models.TextField(blank=True, null=True)
    is_restyle = models.TextField(blank=True, null=True)
    configuration_id = models.TextField(blank=True, null=True)
    doors_count = models.TextField(blank=True, null=True)
    body_type = models.TextField(blank=True, null=True)
    notice = models.TextField(blank=True, null=True)
    complectation_id = models.TextField(blank=True, null=True)
    offers_price_from = models.TextField(blank=True, null=True)
    offers_price_to = models.TextField(blank=True, null=True)
    group_name = models.TextField(blank=True, null=True)
    back_brake = models.TextField(blank=True, null=True)
    feeding = models.TextField(blank=True, null=True)
    horse_power = models.TextField(blank=True, null=True)
    kvt_power = models.TextField(blank=True, null=True)
    rpm_power = models.TextField(blank=True, null=True)
    engine_type = models.TextField(blank=True, null=True)
    transmission = models.TextField(blank=True, null=True)
    drive = models.TextField(blank=True, null=True)
    volume = models.TextField(blank=True, null=True)
    time_to_100 = models.TextField(blank=True, null=True)
    cylinders_order = models.TextField(blank=True, null=True)
    max_speed = models.TextField(blank=True, null=True)
    compression = models.TextField(blank=True, null=True)
    cylinders_value = models.TextField(blank=True, null=True)
    diametr = models.TextField(blank=True, null=True)
    piston_stroke = models.TextField(blank=True, null=True)
    engine_feeding = models.TextField(blank=True, null=True)
    engine_order = models.TextField(blank=True, null=True)
    gear_value = models.TextField(blank=True, null=True)
    moment = models.TextField(blank=True, null=True)
    petrol_type = models.TextField(blank=True, null=True)
    valves = models.TextField(blank=True, null=True)
    weight = models.TextField(blank=True, null=True)
    wheel_size = models.TextField(blank=True, null=True)
    wheel_base = models.TextField(blank=True, null=True)
    front_wheel_base = models.TextField(blank=True, null=True)
    back_wheel_base = models.TextField(blank=True, null=True)
    front_brake = models.TextField(blank=True, null=True)
    front_suspension = models.TextField(blank=True, null=True)
    back_suspension = models.TextField(blank=True, null=True)
    height = models.TextField(blank=True, null=True)
    width = models.TextField(blank=True, null=True)
    fuel_tank_capacity = models.TextField(blank=True, null=True)
    seats = models.TextField(blank=True, null=True)
    length = models.TextField(blank=True, null=True)
    emission_euro_class = models.TextField(blank=True, null=True)
    volume_litres = models.TextField(blank=True, null=True)
    consumption_mixed = models.TextField(blank=True, null=True)
    clearance = models.TextField(blank=True, null=True)
    trunks_min_capacity = models.TextField(blank=True, null=True)
    trunks_max_capacity = models.TextField(blank=True, null=True)
    consumption_hiway = models.TextField(blank=True, null=True)
    consumption_city = models.TextField(blank=True, null=True)
    moment_rpm = models.TextField(blank=True, null=True)
    full_weight = models.TextField(blank=True, null=True)
    range_distance = models.TextField(blank=True, null=True)
    battery_capacity = models.TextField(blank=True, null=True)
    fuel_emission = models.TextField(blank=True, null=True)
    electric_range = models.TextField(blank=True, null=True)
    charge_time = models.TextField(blank=True, null=True)
    safety_rating = models.TextField(blank=True, null=True)
    safety_grade = models.TextField(blank=True, null=True)
    alcantara = models.TextField(blank=True, null=True)
    black_roof = models.TextField(blank=True, null=True)
    combo_interior = models.TextField(blank=True, null=True)
    decorative_interior_lighting = models.TextField(blank=True, null=True)
    door_sill_panel = models.TextField(blank=True, null=True)
    driver_seat_electric = models.TextField(blank=True, null=True)
    driver_seat_memory = models.TextField(blank=True, null=True)
    driver_seat_support = models.TextField(blank=True, null=True)
    driver_seat_updown = models.TextField(blank=True, null=True)
    eco_leather = models.TextField(blank=True, null=True)
    electro_rear_seat = models.TextField(blank=True, null=True)
    fabric_seats = models.TextField(blank=True, null=True)
    folding_front_passenger_seat = models.TextField(blank=True, null=True)
    folding_tables_rear = models.TextField(blank=True, null=True)
    front_centre_armrest = models.TextField(blank=True, null=True)
    front_seat_support = models.TextField(blank=True, null=True)
    front_seats_heat = models.TextField(blank=True, null=True)
    front_seats_heat_vent = models.TextField(blank=True, null=True)
    hatch = models.TextField(blank=True, null=True)
    leather = models.TextField(blank=True, null=True)
    leather_gear_stick = models.TextField(blank=True, null=True)
    massage_seats = models.TextField(blank=True, null=True)
    panorama_roof = models.TextField(blank=True, null=True)
    passenger_seat_electric = models.TextField(blank=True, null=True)
    passenger_seat_updown = models.TextField(blank=True, null=True)
    rear_seat_heat_vent = models.TextField(blank=True, null=True)
    rear_seat_memory = models.TextField(blank=True, null=True)
    rear_seats_heat = models.TextField(blank=True, null=True)
    roller_blind_for_rear_window = models.TextField(blank=True, null=True)
    roller_blinds_for_rear_side_windows = models.TextField(blank=True, null=True)
    seat_memory = models.TextField(blank=True, null=True)
    seat_transformation = models.TextField(blank=True, null=True)
    sport_pedals = models.TextField(blank=True, null=True)
    sport_seats = models.TextField(blank=True, null=True)
    third_rear_headrest = models.TextField(blank=True, null=True)
    third_row_seats = models.TextField(blank=True, null=True)
    tinted_glass = models.TextField(blank=True, null=True)
    wheel_heat = models.TextField(blank=True, null=True)
    wheel_leather = models.TextField(blank=True, null=True)
    col_360_camera = models.TextField(db_column='col_360-camera', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    adj_pedals = models.TextField(blank=True, null=True)
    ashtray_and_cigarette_lighter = models.TextField(blank=True, null=True)
    auto_cruise = models.TextField(blank=True, null=True)
    auto_mirrors = models.TextField(blank=True, null=True)
    auto_park = models.TextField(blank=True, null=True)
    climate_control_1 = models.TextField(blank=True, null=True)
    climate_control_2 = models.TextField(blank=True, null=True)
    computer = models.TextField(blank=True, null=True)
    condition = models.TextField(blank=True, null=True)
    cooling_box = models.TextField(blank=True, null=True)
    cruise_control = models.TextField(blank=True, null=True)
    drive_mode_sys = models.TextField(blank=True, null=True)
    e_adjustment_wheel = models.TextField(blank=True, null=True)
    easy_trunk_opening = models.TextField(blank=True, null=True)
    electro_mirrors = models.TextField(blank=True, null=True)
    electro_trunk = models.TextField(blank=True, null=True)
    electro_window_back = models.TextField(blank=True, null=True)
    electro_window_front = models.TextField(blank=True, null=True)
    electronic_gage_panel = models.TextField(blank=True, null=True)
    front_camera = models.TextField(blank=True, null=True)
    keyless_entry = models.TextField(blank=True, null=True)
    multi_wheel = models.TextField(blank=True, null=True)
    multizone_climate_control = models.TextField(blank=True, null=True)
    park_assist_f = models.TextField(blank=True, null=True)
    park_assist_r = models.TextField(blank=True, null=True)
    power_latching_doors = models.TextField(blank=True, null=True)
    programmed_block_heater = models.TextField(blank=True, null=True)
    projection_display = models.TextField(blank=True, null=True)
    rear_camera = models.TextField(blank=True, null=True)
    remote_engine_start = models.TextField(blank=True, null=True)
    servo = models.TextField(blank=True, null=True)
    start_button = models.TextField(blank=True, null=True)
    start_stop_function = models.TextField(blank=True, null=True)
    steering_wheel_gear_shift_paddles = models.TextField(blank=True, null=True)
    wheel_configuration1 = models.TextField(blank=True, null=True)
    wheel_configuration2 = models.TextField(blank=True, null=True)
    wheel_memory = models.TextField(blank=True, null=True)
    wheel_power = models.TextField(blank=True, null=True)
    adaptive_light = models.TextField(blank=True, null=True)
    automatic_lighting_control = models.TextField(blank=True, null=True)
    drl = models.TextField(blank=True, null=True)
    heated_wash_system = models.TextField(blank=True, null=True)
    high_beam_assist = models.TextField(blank=True, null=True)
    laser_lights = models.TextField(blank=True, null=True)
    led_lights = models.TextField(blank=True, null=True)
    light_cleaner = models.TextField(blank=True, null=True)
    light_sensor = models.TextField(blank=True, null=True)
    mirrors_heat = models.TextField(blank=True, null=True)
    ptf = models.TextField(blank=True, null=True)
    rain_sensor = models.TextField(blank=True, null=True)
    windcleaner_heat = models.TextField(blank=True, null=True)
    windscreen_heat = models.TextField(blank=True, null=True)
    xenon = models.TextField(blank=True, null=True)
    abs = models.TextField(blank=True, null=True)
    airbag_curtain = models.TextField(blank=True, null=True)
    airbag_driver = models.TextField(blank=True, null=True)
    airbag_passenger = models.TextField(blank=True, null=True)
    airbag_rear_side = models.TextField(blank=True, null=True)
    airbag_side = models.TextField(blank=True, null=True)
    asr = models.TextField(blank=True, null=True)
    bas = models.TextField(blank=True, null=True)
    blind_spot = models.TextField(blank=True, null=True)
    collision_prevention_assist = models.TextField(blank=True, null=True)
    dha = models.TextField(blank=True, null=True)
    drowsy_driver_alert_system = models.TextField(blank=True, null=True)
    esp = models.TextField(blank=True, null=True)
    feedback_alarm = models.TextField(blank=True, null=True)
    glonass = models.TextField(blank=True, null=True)
    hcc = models.TextField(blank=True, null=True)
    isofix = models.TextField(blank=True, null=True)
    isofix_front = models.TextField(blank=True, null=True)
    knee_airbag = models.TextField(blank=True, null=True)
    laminated_safety_glass = models.TextField(blank=True, null=True)
    lane_keeping_assist = models.TextField(blank=True, null=True)
    night_vision = models.TextField(blank=True, null=True)
    power_child_locks_rear_doors = models.TextField(blank=True, null=True)
    traffic_sign_recognition = models.TextField(blank=True, null=True)
    tyre_pressure = models.TextField(blank=True, null=True)
    vsm = models.TextField(blank=True, null=True)
    alarm = models.TextField(blank=True, null=True)
    immo = models.TextField(blank=True, null=True)
    lock = models.TextField(blank=True, null=True)
    volume_sensor = models.TextField(blank=True, null=True)
    col_12v_socket = models.TextField(db_column='col_12v-socket', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    col_220v_socket = models.TextField(db_column='col_220v-socket', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    android_auto = models.TextField(blank=True, null=True)
    apple_carplay = models.TextField(blank=True, null=True)
    audiopreparation = models.TextField(blank=True, null=True)
    audiosystem_cd = models.TextField(blank=True, null=True)
    audiosystem_tv = models.TextField(blank=True, null=True)
    aux = models.TextField(blank=True, null=True)
    bluetooth = models.TextField(blank=True, null=True)
    entertainment_system_for_rear_seat_passengers = models.TextField(blank=True, null=True)
    music_super = models.TextField(blank=True, null=True)
    navigation = models.TextField(blank=True, null=True)
    usb = models.TextField(blank=True, null=True)
    voice_recognition = models.TextField(blank=True, null=True)
    wireless_charger = models.TextField(blank=True, null=True)
    ya_auto = models.TextField(blank=True, null=True)
    activ_suspension = models.TextField(blank=True, null=True)
    air_suspension = models.TextField(blank=True, null=True)
    reduce_spare_wheel = models.TextField(blank=True, null=True)
    spare_wheel = models.TextField(blank=True, null=True)
    sport_suspension = models.TextField(blank=True, null=True)
    col_14_inch_wheels = models.TextField(db_column='col_14-inch-wheels', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    col_15_inch_wheels = models.TextField(db_column='col_15-inch-wheels', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    col_16_inch_wheels = models.TextField(db_column='col_16-inch-wheels', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    col_17_inch_wheels = models.TextField(db_column='col_17-inch-wheels', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    col_18_inch_wheels = models.TextField(db_column='col_18-inch-wheels', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    col_19_inch_wheels = models.TextField(db_column='col_19-inch-wheels', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    col_20_inch_wheels = models.TextField(db_column='col_20-inch-wheels', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    col_21_inch_wheels = models.TextField(db_column='col_21-inch-wheels', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    col_22_inch_wheels = models.TextField(db_column='col_22-inch-wheels', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    body_kit = models.TextField(blank=True, null=True)
    body_mouldings = models.TextField(blank=True, null=True)
    duo_body_color = models.TextField(blank=True, null=True)
    paint_metallic = models.TextField(blank=True, null=True)
    roof_rails = models.TextField(blank=True, null=True)
    steel_wheels = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cars_data_test'


