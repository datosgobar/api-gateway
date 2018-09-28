from django.conf.urls import url
from rest_framework import routers

from .views import QueryViewSet, query_swagger_view, download_csv_view

router = routers.SimpleRouter()  # pylint: disable=invalid-name
router.register(r'queries', QueryViewSet)

urlpatterns = router.urls  # pylint: disable=invalid-name

urlpatterns += [
    url(r'^queries/swagger/$', query_swagger_view, name='query-swagger'),
    url(r'^(?P<api_name>[a-z]{1,30}.+)/analytics_(?P<date>\d{4}-\d{2}-\d{2}).csv$',
        download_csv_view,
        name='download-csv'),
]
