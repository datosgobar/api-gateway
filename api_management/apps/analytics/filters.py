from django_filters import rest_framework as filters
from api_management.apps.analytics.models import Query


class QueryFilter(filters.FilterSet):

    kong_api_id = filters.NumberFilter(field_name='api_data', lookup_expr='id')
    from_date = filters.DateTimeFilter(field_name='start_time', lookup_expr='gt')
    to_date = filters.DateTimeFilter(field_name='start_time', lookup_expr='lt')

    class Meta:
        model = Query
        fields = (
            'kong_api_id',
            'from_date',
            'to_date',
        )
