from rest_framework import routers

from .views import QueryViewSet

router = routers.SimpleRouter()  # pylint: disable=invalid-name
router.register(r'queries', QueryViewSet)

urlpatterns = router.urls  # pylint: disable=invalid-name
