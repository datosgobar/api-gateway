from django.conf.urls import url
from rest_framework import routers

from .views import QueryViewSet, query_swagger_view

router = routers.SimpleRouter()  # pylint: disable=invalid-name
router.register(r'queries', QueryViewSet)

urlpatterns = router.urls  # pylint: disable=invalid-name

urlpatterns += [
    url(r'^queries/swagger/$', query_swagger_view, name='query-swagger'),
]
