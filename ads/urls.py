from django.urls import path
from .views import (ad_list, ad_detail, ad_create, profile_view,
                    ad_edit, home, search_ads, get_models, delete_image,
                    ad_delete, )
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("", home, name="home"),  # Главная страница с поиском
    path("ads/", ad_list, name="ad_list"),
    path("ad/<str:source>/<int:ad_id>/", ad_detail, name="ad_detail"),
    path("ad/new/", ad_create, name="ad_create"),
    path("profile/", profile_view, name="profile"),  # Страница профиля
    path("ad/<str:source>/<int:ad_id>/edit/", ad_edit, name="ad_edit"),  # Редактирование объявления
    path("search/", search_ads, name="search_ads"),
    path("get_models/", get_models, name="get_models"),
    path("delete-image/<int:image_id>/", delete_image, name="delete_image"),
    path('ad/<int:ad_id>/delete/', ad_delete, name='ad_delete'),



]