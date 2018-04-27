import datetime
from abc import abstractmethod

from django.core.exceptions import ImproperlyConfigured
from rest_framework.filters import BaseFilterBackend


class KongApiIdFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        kong_api_id = request.query_params.get('kong_api_id', None)

        if kong_api_id is not None:
            return queryset.filter(api_data__id=kong_api_id)

        return queryset


class BaseDateFilterBackend(BaseFilterBackend):

    query_param = None

    def filter_queryset(self, request, queryset, view):
        date = request.query_params.get(self.get_query_param(), None)
        if date is not None:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')

            return self.perform_filter(queryset, date)

        return queryset

    @staticmethod
    @abstractmethod
    def perform_filter(queryset, start_time):
        pass

    def get_query_param(self):
        if self.query_param is None:
            raise ImproperlyConfigured('query_param not configured')

        return self.query_param


class FromBaseDateFilterBackend(BaseDateFilterBackend):

    query_param = 'from'

    @staticmethod
    def perform_filter(queryset, start_time):
        return queryset.filter(start_time__gt=start_time)


class ToBaseDateFilterBackend(BaseDateFilterBackend):

    query_param = 'to'

    @staticmethod
    def perform_filter(queryset, start_time):
        return queryset.filter(start_time__lt=start_time)
