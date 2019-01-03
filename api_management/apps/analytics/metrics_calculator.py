from datetime import date

from api_management.apps.analytics.models import generate_api_session_id, IndicatorMetricsRow, \
    Query, next_day_of


class IndicatorMetricsCalculator:

    def __init__(self, api_name):
        self.api_name = api_name

    def is_mobile(self, user_agent):
        return "Mobile" in user_agent or \
               "Android" in user_agent or \
               "iPhone" in user_agent or \
               "Slackbot" in user_agent

    def indicator_row_content(self, queries):
        unique_session_ids = set()
        total_mobile = 0
        total_not_mobile = 0

        for query in queries:
            unique_session_ids.add(generate_api_session_id(query))

            if self.is_mobile(query.user_agent):
                total_mobile = total_mobile + 1
            else:
                total_not_mobile = total_not_mobile + 1

        return {'total': total_mobile + total_not_mobile,
                'total_mobile': total_mobile,
                'total_not_mobile': total_not_mobile,
                'total_unique_users': len(unique_session_ids)}

    def first_query_time(self):
        query_time = Query.objects.first().start_time.date()
        last_row = IndicatorMetricsRow.objects.filter(api_name=self.api_name).last()
        if last_row is not None:
            query_time = next_day_of(last_row.date)

        return query_time

    def drop_metric_rows(self, force):
        if force:
            IndicatorMetricsRow.objects.filter(api_name=self.api_name).delete()

    def calculate_indicators(self, queries, row_date):
        total_counts = self.indicator_row_content(queries)

        indicator_row = IndicatorMetricsRow(api_name=self.api_name)
        indicator_row.date = row_date
        indicator_row.all_queries = total_counts.get('total')
        indicator_row.all_mobile = total_counts.get('total_mobile')
        indicator_row.all_not_mobile = total_counts.get('total_not_mobile')
        indicator_row.total_users = total_counts.get('total_unique_users')
        indicator_row.save()

    def calculate(self, force):
        self.drop_metric_rows(force)
        query_time = self.first_query_time()

        while query_time < date.today():
            queries = self.all_queries(query_time)
            self.calculate_indicators(queries, query_time)
            query_time = next_day_of(query_time)

    def all_queries(self, query_time):
        return Query.objects.filter(api_data__name=self.api_name,
                                    start_time__gte=query_time,
                                    start_time__lt=next_day_of(query_time))\
                            .exclude(request_method='OPTIONS')
