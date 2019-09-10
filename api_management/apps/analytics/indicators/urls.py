from django.conf.urls import url

from api_management.apps.analytics.views import download_indicators_csv_view

urlpatterns = [
    url(r'^indicadores-(?P<api_endpoint>[a-z]{1,30}.+).csv$',
        download_indicators_csv_view,
        name='download-indicators-csv')
]