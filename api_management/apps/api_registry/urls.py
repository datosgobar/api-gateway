from rest_framework.urls import url

from .views import DocsView, TokenRequestView, root_redirect

urlpatterns = [
    url(r'^docs/(?P<name>.+)/$', DocsView.as_view(), name='api-doc'),
    url(r'^token-request/(?P<name>.+)/$', TokenRequestView.as_view(), name='token-request'),
    url(r'^root_url/$', root_redirect, name='root-redirect')
]
