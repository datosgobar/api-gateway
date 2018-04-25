import datetime

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

from .models import Query
from .serializers import QuerySerializer
from .tasks import make_model_object


class QueryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):

    pagination_class = LimitOffsetPagination
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]

    def create(self, request, *args, **kwargs):
        super(QueryViewSet, self).create(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        make_model_object.delay(serializer.data, type(serializer))

    def get_queryset(self):
        queryset = Query.objects.all()

        kong_api_id = self.request.query_params.get('kong_api_id', None)
        if kong_api_id is not None:
            queryset = queryset.filter(api_data__id=kong_api_id)

        from_start_time = self.request.query_params.get('from', None)
        if from_start_time is not None:
            from_start_time = datetime.datetime.strptime(from_start_time, '%Y-%m-%d')
            queryset = queryset.filter(start_time__gt=from_start_time)

        to_start_time = self.request.query_params.get('to', None)
        if to_start_time is not None:
            to_start_time = datetime.datetime.strptime(to_start_time, '%Y-%m-%d')
            queryset = queryset.filter(start_time__lt=to_start_time)

        return queryset
