from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django_filters import rest_framework as filters
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from api_management.apps.analytics import swaggers
from api_management.apps.api_registry.models import KongApi
from .filters import QueryFilter
from .models import Query, CsvFile, ZipFile
from .serializers import QuerySerializer
from .tasks import make_model_object


class QueryViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    class CustomPagination(CursorPagination):
        page_size = 1000

    pagination_class = CustomPagination
    filter_backends = [
        filters.DjangoFilterBackend,
        OrderingFilter,
    ]
    filter_class = QueryFilter
    queryset = Query.objects.all()
    serializer_class = QuerySerializer
    permission_classes = [IsAdminUser, ]
    authentication_classes = [TokenAuthentication, ]
    ordering_fields = ('id', 'start_time', 'request_time', )
    ordering = ('id', )

    def create(self, request, *args, **kwargs):
        super(QueryViewSet, self).create(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        make_model_object.delay(serializer.data, type(serializer))


@api_view(['GET'])
def query_swagger_view(*_, **__):
    return Response(swaggers.QUERIES)


def make_response_for_file(response, files):
    if files.exists() and files.first().file is not None:
        response['Content-Disposition'] = "attachment;" \
                                          "filename={name}".format(name=files.first().file_name)
        response.content_type = 'text/csv'
        response.content = files.first().file
    else:
        response.status_code = 501
    return response


@api_view(['GET'])
@login_required
def download_csv_view(_request, api_name, date):
    response = HttpResponse()

    if not KongApi.objects.filter(name=api_name).exists():
        response.status_code = 404
        return response

    files = CsvFile.objects.filter(type="analytics",
                                   api_name=api_name,
                                   file_name="analytics_{date}.csv".format(date=date))

    return make_response_for_file(response, files)


@api_view(['GET'])
def download_indicators_csv_view(_request, api_endpoint):
    response = HttpResponse()

    if not KongApi.objects.filter(uri=api_endpoint).exists():
        response.status_code = 404
        return response

    api_name = KongApi.objects.get(uri=api_endpoint).name

    files = CsvFile.objects.filter(type="indicators",
                                   api_name=api_name,
                                   file_name="indicadores-{endpoint}.csv".format(
                                       endpoint=api_endpoint))

    return make_response_for_file(response, files)


@api_view(['GET'])
def download_zip_view(_request, api_name, date):
    response = HttpResponse()

    if not KongApi.objects.filter(name=api_name).exists():
        response.status_code = 404
        return response

    zip_file = ZipFile.objects.filter(api_name=api_name,
                                      file_name="analytics_{date}.zip".format(date=date)).first()

    if zip_file is not None:
        response['Content-Disposition'] = "attachment;" \
                                          "filename={name}".format(name=zip_file.file_name)
        response.content_type = 'application/zip'
        response.content = zip_file.file
    else:
        response.status_code = 501

    return response
