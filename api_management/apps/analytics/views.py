
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination as DRFLimitOffsetPagination

from .models import Query
from .serializers import QuerySerializer
from .tasks import make_model_object
from .filters import KongApiIdFilterBackend, \
    FromBaseDateFilterBackend, ToBaseDateFilterBackend


class LimitOffsetPagination(DRFLimitOffsetPagination):
    default_limit = 10
    max_limit = 1000


class QueryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):

    pagination_class = LimitOffsetPagination
    filter_backends = [
        KongApiIdFilterBackend,
        FromBaseDateFilterBackend,
        ToBaseDateFilterBackend,
    ]
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]

    def create(self, request, *args, **kwargs):
        super(QueryViewSet, self).create(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        make_model_object.delay(serializer.data, type(serializer))
