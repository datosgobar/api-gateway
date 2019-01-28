from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections

from api_management.apps.analytics.models import Query
from api_management.apps.elastic_search.models import QueryIndex

connections.create_connection(alias='default', hosts=[settings.ELASTIC_SEARCH_HOST])


def bulk_index():
    QueryIndex.init(index='query-index')
    client = Elasticsearch()
    bulk(client=client, actions=(b.index() for b in Query.objects.all().iterator()))
