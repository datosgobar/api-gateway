from django.conf.urls import url, include
from django.urls import path

from rest_framework.authtoken import views as authtoken_views

from .views import create_query

urlpatterns = [  # pylint: disable=invalid-name
    path('queries/', create_query),
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
    url(r'^token/', authtoken_views.obtain_auth_token)
]
