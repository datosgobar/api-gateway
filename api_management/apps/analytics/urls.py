from django.urls import path

from .views import create_query

urlpatterns = [  # pylint: disable=invalid-name
    path('queries/', create_query),
]
