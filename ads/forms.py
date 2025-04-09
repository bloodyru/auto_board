from django import forms
from .models import Ad, CarsDataTest, Profile
import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.cache import cache


class InlineRadioWidget(forms.RadioSelect):
    template_name = 'widgets/inline_radio.html'


class AdForm(forms.ModelForm):
    mark_names = forms.ChoiceField(
        choices=[],
        required=True,
        label="Марка",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_mark_name"})
    )

    model = forms.ChoiceField(
        choices=[],
        required=True,
        label="Модель",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_model_name"})
    )

    year = forms.IntegerField(
        min_value=1950,
        max_value=datetime.datetime.now().year,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Год выпуска"}),
        label="Год выпуска"
    )

    class Meta:
        model = Ad
        fields = ["mark_names", "model", "year", "price", "mileage",
                  "fuel_type", "gearbox", "body_type", "seller", "drive",
                  "location", "damaged", "steering", "color", "documents", "exchange", "description"]
        labels = {
            "year": "Год выпуска",
            "mileage": "Пробег (км)",
            "price": "Цена (₽)",
            "description": "Описание",
        }
        widgets = {
            "mileage": forms.NumberInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": "3"}),
            "fuel_type": forms.Select(attrs={"class": "form-select"}),
            "gearbox": forms.Select(attrs={"class": "form-select"}),
            "body_type": forms.Select(attrs={"class": "form-select"}),
            "seller": forms.Select(attrs={"class": "form-select"}),
            "drive": forms.Select(attrs={"class": "form-select"}),
            "location": forms.Select(attrs={"class": "form-select"}),
            "damaged": forms.Select(attrs={"class": "form-select"}),
            "steering": forms.Select(attrs={"class": "form-select"}),
            "color": InlineRadioWidget(attrs={"class": "form-check form-check-inline"}),
            "documents": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ключ для кэша
        CACHE_KEY_MARKS = 'car_marks_list'

        # Пытаемся получить данные из кэша
        marks = cache.get(CACHE_KEY_MARKS)

        if marks is None:
            # Если в кэше нет данных, загружаем из базы и сохраняем в кэш
            marks = list(CarsDataTest.objects.values_list("mark_name", flat=True)
            .distinct().order_by("mark_name"))
            cache.set(CACHE_KEY_MARKS, marks, 60 * 60 * 24)  # Кэшируем на 24 часа

        # Загружаем список марок авто
        self.fields["mark_names"].choices = [(i, i) for i in marks]

        # Загружаем модели авто
        selected_mark = self.data.get("mark_names") or (self.instance.mark_names if self.instance else None)
        if selected_mark:
            model_choices = [
                (m, m) for m in CarsDataTest.objects.filter(mark_name=selected_mark)
                .values_list("model_name", flat=True).distinct()
            ]
            selected_model = self.data.get("model") or (self.instance.model if self.instance else None)

            # ✅ Если выбранная модель не в списке, добавляем её
            if selected_model and (selected_model, selected_model) not in model_choices:
                model_choices.append((selected_model, selected_model))

            self.fields["model"].choices = model_choices
        else:
            self.fields["model"].choices = [("", "Выберите модель")]

# FUEL_TYPE_MAPPING = {
#     'бензин': 'petrol',
#     'дизель': 'diesel',
#     'СУГ': 'gas',
#     'электро': 'electric',
#     'гибрид': 'hybrid',
#     'гидроген': 'hydrogen'  # Добавьте это значение в FUEL_TYPE_CHOICES если нужно
# }
#
# # Обратное преобразование для отображения
# FUEL_TYPE_REVERSE_MAPPING = {v: k for k, v in FUEL_TYPE_MAPPING.items()}


def clean_model(self):
        model = self.cleaned_data.get("model")
        mark_name = self.cleaned_data.get("mark_names")
        print("1111111111111111111111111")
        if mark_name and model:
            if not CarsDataTest.objects.filter(mark_name=mark_name, model_name=model).exists():
                raise forms.ValidationError("Выбранная модель не соответствует выбранной марке.")

        return model


class ProfileForm(forms.ModelForm):
    # Добавляем поле username из модели User
    username = forms.CharField(max_length=150, label="Имя пользователя")

    class Meta:
        model = Profile
        fields = ["contact_number"]  # Убрали avatar
        labels = {
            "contact_number": "Телефон",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем начальное значение для username
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Сохраняем username в связанной модели User
        if 'username' in self.cleaned_data:
            profile.user.username = self.cleaned_data['username']
            if commit:
                profile.user.save()
        if commit:
            profile.save()
        return profile

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_password2(self):
        """Проверка совпадения паролей"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2
