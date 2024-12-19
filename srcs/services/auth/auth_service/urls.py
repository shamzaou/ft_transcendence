"""
URL configuration for auth_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.http import HttpResponseNotFound
from auth_service.views import register_view, login_view, redirect_uri, get_user_info, oauth_callback
from . import views
from django.conf import settings
from django.conf.urls.static import static
 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('homepage/', views.homepage_view, name='homepage'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', views.register_user, name='register_user'),
    path('', views.homepage_view, name='root'),
    path('api/redirect_uri/', redirect_uri, name='redirect_uri'),
    path('api/oauth_callback/', oauth_callback, name='oauth_callback'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def custom_404(request, exception):
    return HttpResponseNotFound('<h1>Page not found</h1>')

handler404 = 'auth_service.urls.custom_404'