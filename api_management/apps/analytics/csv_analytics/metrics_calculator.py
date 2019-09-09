from datetime import date

from django.db.models import Q

from api_management.apps.analytics.elastic_search.aggregations import Aggregations
from api_management.apps.analytics.elastic_search.query_search import QuerySearch
from api_management.apps.analytics.models import IndicatorMetricsRow, Query, next_day_of


class IndicatorMetricsCalculator:

    def __init__(self, api_name):
        self.api_name = api_name

    def first_query_time(self):
        query_time = Query.objects.filter(api_data__name=self.api_name) \
            .order_by('start_time').first().start_time.date()
        last_row = IndicatorMetricsRow.objects.filter(api_name=self.api_name).last()
        if last_row is not None:
            query_time = next_day_of(last_row.date)

        return query_time

    def no_queries(self):
        return not Query.objects.filter(api_data__name=self.api_name).exists()

    def drop_metric_rows(self, force):
        if force:
            IndicatorMetricsRow.objects.filter(api_name=self.api_name).delete()

    def total_mobile_queries(self, queries):
        return queries.filter(Q(user_agent__icontains="Mobile") |
                              Q(user_agent__icontains="Android") |
                              Q(user_agent__icontains="iPhone") |
                              Q(user_agent__icontains="Slackbot")).count()

    def generate_unique_users_query(self, queries):
        search = QuerySearch()
        search.add_terms_filter('_id', list(queries.values_list('id', flat=True)))
        search.add_aggregation('unique_users', Aggregations.cardinality('api_session_id'))

        return search

    def total_unique_users(self, queries):
        result = self.generate_unique_users_query(queries).execute()

        return result.aggregations.unique_users.value

    def calculate_indicators(self, row_date):
        queries = self.all_queries(row_date)
        mobile_count = self.total_mobile_queries(queries)

        indicator_row = IndicatorMetricsRow(api_name=self.api_name)
        indicator_row.date = row_date
        indicator_row.all_queries = queries.count()
        indicator_row.all_mobile = mobile_count
        indicator_row.all_not_mobile = indicator_row.all_queries - mobile_count
        indicator_row.total_users = self.total_unique_users(queries)
        indicator_row.save()

    def calculate(self, force):
        if self.no_queries():
            return

        self.drop_metric_rows(force)
        self.perform_calculate(self.first_query_time())

    def perform_calculate(self, query_time):
        while query_time < date.today():
            self.calculate_indicators(query_time)
            query_time = next_day_of(query_time)

    def all_queries(self, query_time):
        return Query.objects.all_without_options().filter(api_data__name=self.api_name,
                                                          start_time__gte=query_time,
                                                          start_time__lt=next_day_of(query_time))
