from elasticsearch_dsl import A

from api_management.apps.analytics.elastic_search.query_index import QueryIndex


class QuerySearch:

    def __init__(self):
        self.search = QueryIndex.search(index='query')

    def add_terms_filter(self, field: str, values):
        self.search = self.search.filter('terms', **{field: values})

    def add_aggregation(self, name: str, aggregation: A):
        self.search.aggs.bucket(name, aggregation)

    def execute(self):
        return self.search.execute()
