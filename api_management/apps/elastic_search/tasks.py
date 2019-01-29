from django_rq import job

from api_management.apps.elastic_search.setup import bulk_index


@job('index_all')
def index_all():
    bulk_index()
