from api_management.apps.analytics.elastic_search.query_index import index_query


class QueryRepository:

    def __init__(self, query_serializer):
        self.query_serializer = query_serializer
        self.query_instance = None

    def save(self):
        self._save_to_db()
        self._index_to_es()

    def _save_to_db(self):
        self.query_serializer.is_valid(raise_exception=True)
        instance = self.query_serializer.save()
        self.query_instance = instance

    def _index_to_es(self):
        index_query(self.query_instance)
