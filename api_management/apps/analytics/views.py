
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination as DRFLimitOffsetPagination
from django_filters import rest_framework as filters

from .metadatas import QueryMetadata
from .models import Query
from .serializers import QuerySerializer
from .tasks import make_model_object
from .filters import QueryFilter


class LimitOffsetPagination(DRFLimitOffsetPagination):
    default_limit = 10
    max_limit = 1000


class QueryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):

    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.DjangoFilterBackend,
    ]
    filter_class = QueryFilter
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]
    metadata_class = QueryMetadata

    def create(self, request, *args, **kwargs):
        super(QueryViewSet, self).create(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        make_model_object.delay(serializer.data, type(serializer))


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def query_swagger(request):
    self = QueryViewSet()
    meta = self.metadata_class()
    data = meta.determine_metadata(request, self)
    return Response(data)
