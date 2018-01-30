from django.urls import path
from rest_framework.authtoken import views as authtoken_views

from .views import create_query

urlpatterns = [  # pylint: disable=invalid-name
    path('queries/', create_query),
    path('token/', authtoken_views.obtain_auth_token)
]
