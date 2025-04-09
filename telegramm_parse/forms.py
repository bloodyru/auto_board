from django import forms
from .models import TelegramAd
#
# class TelegramAdForm(forms.ModelForm):
#     class Meta:
#         model = TelegramAd
#         fields = [
#             "message_id", "text", "date_posted", "photo_url",
#             "brand", "model", "year", "mileage", "contact_number"
#         ]
#         widgets = {
#             "date_posted": forms.DateTimeInput(attrs={"type": "datetime-local"}),
#             "text": forms.Textarea(attrs={"rows": 4, "cols": 40}),
#             "photo_url": forms.TextInput(attrs={"placeholder": "Ссылка на фото"}),
#             "contact_number": forms.TextInput(attrs={"placeholder": "+7XXXXXXXXXX"}),
#         }
