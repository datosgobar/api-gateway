from datetime import date
from django.db.models import Q
from elasticsearch_dsl import A

from api_management.apps.analytics.elastic_search.query_index import QueryIndex
from api_management.apps.analytics.models import IndicatorMetricsRow, Query, next_day_of
from api_management.apps.analytics.repositories.query_repository import QueryRepository


class IndicatorMetricsCalculator:

    def __init__(self, api_name):
        self.api_name = api_name

    def first_query_time(self):
        query_time = Query.objects.filter(api_data__name=self.api_name).first().start_time.date()
        last_row = IndicatorMetricsRow.objects.filter(api_name=self.api_name).last()
        if last_row is not None:
            query_time = next_day_of(last_row.date)

        return query_time

    def drop_metric_rows(self, force):
        if force:
            IndicatorMetricsRow.objects.filter(api_name=self.api_name).delete()

    def calculate_indicators(self, row_date):
        queries = self.all_queries(row_date)
        mobile_count = queries.filter(Q(user_agent__icontains="Mobile") |
                                      Q(user_agent__icontains="Android") |
                                      Q(user_agent__icontains="iPhone") |
                                      Q(user_agent__icontains="Slackbot")).count()

        indicator_row = IndicatorMetricsRow(api_name=self.api_name)
        indicator_row.date = row_date
        indicator_row.all_queries = queries.count()
        indicator_row.all_mobile = mobile_count
        indicator_row.all_not_mobile = indicator_row.all_queries - mobile_count

        aggregation = A('cardinality', field='api_session_id.keyword')
        search = QueryIndex.search(index='query')
        search.filter('terms', _id=queries.values_list('id', flat=True))
        search.aggs.bucket('my_agg', aggregation)
        result = search.execute()

        indicator_row.total_users = result.hits.total
        indicator_row.save()

    def calculate(self, force):
        if not Query.objects.filter(api_data__name=self.api_name).exists():
            return

        self.drop_metric_rows(force)
        query_time = self.first_query_time()

        while query_time < date.today():
            self.calculate_indicators(query_time)
            query_time = next_day_of(query_time)

    def all_queries(self, query_time):
        return QueryRepository.all_without_options().filter(api_data__name=self.api_name,
                                                            start_time__gte=query_time,
                                                            start_time__lt=next_day_of(query_time))
