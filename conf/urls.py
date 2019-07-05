"""sample URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.authtoken import views as authtoken_views
from des import urls as des_urls

admin.autodiscover()
admin.site.index_template = "custom_index.html"
admin.site.login_template = 'login.html'

api_urlpatterns = [
    path('analytics/', include('api_management.apps.analytics.urls')),
    path('registry/', include('api_management.apps.api_registry.urls')),
    path('token/', authtoken_views.obtain_auth_token)
]

urls = [
    path('ingresar/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
    path('django-rq/', include('django_rq.urls')),
    path('django-des/', include(des_urls)),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/', include(('admin_honeypot.urls', 'honey'), namespace='admin_honeypot')),
]

if settings.URLS_PREFIX:
    urlpatterns = [
        path("%s/" % settings.URLS_PREFIX, include(urls)),
    ]
else:
    urlpatterns = urls
