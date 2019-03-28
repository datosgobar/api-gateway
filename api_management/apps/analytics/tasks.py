from django.utils import timezone
from django_rq import job
from elasticsearch.helpers import bulk
from elasticsearch_dsl.connections import connections

from api_management.apps.analytics.csv_analytics.csv_compressor_and_remover \
    import CsvCompressorAndRemover
from api_management.apps.analytics.csv_analytics.csv_generator import AnalyticsCsvGenerator, \
    IndicatorCsvGenerator
from api_management.apps.analytics.csv_analytics.metrics_calculator \
    import IndicatorMetricsCalculator
from api_management.apps.analytics.elastic_search.query_index import QueryIndex, index_query
from api_management.apps.analytics.models import CsvAnalyticsGeneratorTask, \
    IndicatorCsvGeneratorTask, CsvCompressorTask, CsvFile, CsvCompressorAndRemoverTask, Query
from api_management.apps.analytics.repositories.query_repository import QueryRepository
from api_management.apps.api_registry.models import KongApi


@job('create_model')
def make_model_object(data, serializer_class):
    serializer = serializer_class(data=data)
    query_repository = QueryRepository(serializer)
    query_repository.save()


def generate_csv(generator, task_logger, api_name, analytics_date=None):
    try:
        generator.generate()
        task_logger.log_success(api_name, analytics_date)
    except Exception as exception:
        task_logger.log_error(api_name, analytics_date, exception)
        raise exception


@job('generate_analytics', timeout=3600)
def generate_analytics_dump(analytics_date, task_logger=None):
    task_logger = task_logger or CsvAnalyticsGeneratorTask(created_at=timezone.now())

    for api in KongApi.objects.all():
        csv_generator = AnalyticsCsvGenerator(api_name=api.name, analytics_date=analytics_date)
        generate_csv(csv_generator, task_logger, api.name, analytics_date)


@job('generate_indicators_csv', timeout=-1)  # no timeout
def generate_indicators_csv(force, task_logger=None):
    task_logger = task_logger or IndicatorCsvGeneratorTask(created_at=timezone.now())

    for api in KongApi.objects.all():
        IndicatorMetricsCalculator(api.name).calculate(force)
        csv_generator = IndicatorCsvGenerator(api_name=api.name)
        generate_csv(csv_generator, task_logger, api.name, None)


def perform_compress_and_remove(force, api_name, task_logger, local_time):
    csv_compressor = CsvCompressorAndRemover(api_name)
    try:
        if force:
            csv_compressor.compress_all()
        else:
            csv_compressor.compress_single_file(CsvFile.objects.last())

        task_logger.log_success(api_name, local_time)
    except Exception as exception:
        task_logger.log_error(api_name, local_time, exception)
        raise exception

    delete_zipped_files(csv_compressor, api_name, local_time)


def delete_zipped_files(csv_compressor, api_name, local_time):
    task_logger = CsvCompressorAndRemoverTask(created_at=timezone.now())
    try:
        csv_compressor.delete_zipped_files(365*2)
        task_logger.log_success(api_name, local_time)
    except Exception as exception:
        task_logger.log_error(api_name, local_time, exception)
        raise exception


@job('compress_csv_files', timeout=3600)
def compress_csv_files(force, task_logger=None):
    task_logger = task_logger or CsvCompressorTask(created_at=timezone.now())

    for api in KongApi.objects.all():
        perform_compress_and_remove(force, api.name, task_logger, timezone.now())


@job('generate_indicators_csv', timeout=-1)  # misma cola que el job generate_indicators_csv
def index_all():
    client = connections.get_connection()
    client.indices.delete(index='query', ignore_unavailable=True)
    QueryIndex.init(index='query')
    bulk(client=client, actions=(index_query(b) for b in Query.objects.all().iterator()))
