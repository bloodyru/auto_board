from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from ads.views import logout_view, register, get_brands, get_model_specs
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ads.urls")),  # Используем маршруты ads
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register, name="register"),
    path("get_brands/", get_brands, name="get_brands"),
    path('api/get-model-specs/', get_model_specs, name='get_model_specs'),
] + debug_toolbar_urls()

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
