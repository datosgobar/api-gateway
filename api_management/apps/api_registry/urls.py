from rest_framework import routers

from .views import DocsViewSet

router = routers.SimpleRouter()  # pylint: disable=invalid-name
router.register(r'docs', DocsViewSet)

urlpatterns = router.urls  # pylint: disable=invalid-name
