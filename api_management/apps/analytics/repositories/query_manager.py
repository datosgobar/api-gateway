from django.db.models import Manager

from api_management.apps.analytics.elastic_search.query_index import index_query
from api_management.apps.analytics.google_analytics.google_analytics_manager import GoogleAnalyticsManager


class QueryManager(Manager):
    def create_from_serializer(self, serializer):
        serializer.is_valid(raise_exception=True)
        query = serializer.save()
        index_query(query)
        GoogleAnalyticsManager.prepare_send_analytics(True, query)

    def all_without_options(self):
        return self.exclude(request_method='OPTIONS')
