from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser

from .models import Query
from .serializers import QuerySerializer


class QueryViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    A viewset that provides `create` action.

    """
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]
