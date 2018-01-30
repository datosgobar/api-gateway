from rest_framework import routers

from .views import QueryViewSet

router = routers.SimpleRouter()
router.register(r'queries', QueryViewSet)

urlpatterns = router.urls
