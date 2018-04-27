import datetime
from abc import abstractmethod

from django.core.exceptions import ImproperlyConfigured
from rest_framework.filters import BaseFilterBackend


class QueryParamBaseFilterBackend(BaseFilterBackend):

    query_param = None

    def filter_queryset(self, request, queryset, view):
        raw_value = request.query_params.get(self.get_query_param(), None)
        if raw_value is not None:
            digested_value = self.digest_query_value(raw_value)

            return self.perform_filter(queryset, digested_value)

        return queryset

    @staticmethod
    @abstractmethod
    def perform_filter(queryset, digested_value):
        pass

    def get_query_param(self):
        if self.query_param is None:
            raise ImproperlyConfigured('query_param not configured')

        return self.query_param

    @staticmethod
    @abstractmethod
    def digest_query_value(raw_value):
        pass


class KongApiIdFilterBackend(QueryParamBaseFilterBackend):

    query_param = 'kong_api_id'

    @staticmethod
    def digest_query_value(raw_value):
        return raw_value

    @staticmethod
    def perform_filter(queryset, digested_value):
        return queryset.filter(api_data__id=digested_value)


class BaseDateFilterBackend(QueryParamBaseFilterBackend):

    @staticmethod
    @abstractmethod
    def perform_filter(queryset, digested_value):
        pass

    @staticmethod
    def digest_query_value(raw_value):
        return datetime.datetime.strptime(raw_value, '%Y-%m-%d')


class FromDateFilterBackend(BaseDateFilterBackend):

    query_param = 'from'

    @staticmethod
    def perform_filter(queryset, digested_value):
        return queryset.filter(start_time__gt=digested_value)


class ToDateFilterBackend(BaseDateFilterBackend):

    query_param = 'to'

    @staticmethod
    def perform_filter(queryset, digested_value):
        return queryset.filter(start_time__lt=digested_value)
