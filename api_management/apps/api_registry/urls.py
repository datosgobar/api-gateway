from rest_framework.urls import url

from .views import DocsView


urlpatterns = [
    url(r'^docs/(?P<name>.+)/$', DocsView.as_view(), name='item-detail'),
]
