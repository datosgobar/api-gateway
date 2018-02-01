from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Query
from .serializers import QuerySerializer
from .tasks import make_model_object


class QueryViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides `create` action.

    """
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]

    def create(self, request, *args, **kwargs):
        super(QueryViewSet, self).create(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        make_model_object.delay(serializer.validated_data, type(serializer))
