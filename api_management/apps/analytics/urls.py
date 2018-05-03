from django.conf.urls import url
from rest_framework import routers

from api_management.apps.analytics import views

router = routers.SimpleRouter()  # pylint: disable=invalid-name
router.register(r'queries', views.QueryViewSet)

urlpatterns = router.urls  # pylint: disable=invalid-name

urlpatterns += [
    url(r'^queries/swagger/$', views.query_swagger, name='api-doc'),
]
