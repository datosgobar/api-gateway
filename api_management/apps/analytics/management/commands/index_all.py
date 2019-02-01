from django.core.management import BaseCommand
from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections

from api_management.apps.analytics.elastic_search.query_index import QueryIndex, index_query
from api_management.apps.analytics.models import Query


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Indexando objeto Query. Esto tardará...")
        self.index_all()
        self.stdout.write("Indexación terminada con éxito.")

    def index_all(self):
        QueryIndex.init(index='query')
        client = connections.get_connection()
        bulk(client=client, actions=(index_query(b) for b in Query.objects.all().iterator()))
