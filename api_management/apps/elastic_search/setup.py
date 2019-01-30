from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections

from api_management.apps.analytics.models import Query
from api_management.apps.elastic_search.models import QueryIndex, index_query


def bulk_index():
    QueryIndex.init(index='query')
    client = connections.get_connection()
    bulk(client=client, actions=(index_query(b) for b in Query.objects.all().iterator()))
