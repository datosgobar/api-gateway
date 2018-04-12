from rest_framework.urls import url

from .views import DocsView, TokenRequestView

# pylint: disable=invalid-name
urlpatterns = [
    url(r'^docs/(?P<name>.+)/$', DocsView.as_view(), name='api-doc'),
    url(r'^token-request/$', TokenRequestView.as_view(), name='token-request'),
]
