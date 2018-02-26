from rest_framework import viewsets, mixins
from .models import ApiData
from .serializers import ApiDocSerializer


class DocsViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    serializer_class = ApiDocSerializer
    lookup_field = 'name'
    queryset = ApiData.objects.all()
