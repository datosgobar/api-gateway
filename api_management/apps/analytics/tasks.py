from django.utils import timezone
from django_rq import job

from api_management.apps.analytics.csv_compressor import CsvCompressor
from api_management.apps.analytics.csv_generator import AnalyticsCsvGenerator, \
    IndicatorCsvGenerator
from api_management.apps.analytics.metrics_calculator import IndicatorMetricsCalculator
from api_management.apps.analytics.models import CsvAnalyticsGeneratorTask, \
    IndicatorCsvGeneratorTask, CsvCompressorTask, CsvFile
from api_management.apps.api_registry.models import KongApi
from api_management.apps.common.utils import as_local_datetime


@job('create_model')
def make_model_object(data, serializer_class):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()


def generate_csv(generator, task_logger, api_name, analytics_date=None):
    try:
        generator.generate()
        task_logger.log_success(api_name, analytics_date)
    except Exception as exception:
        task_logger.log_error(api_name, analytics_date, exception)
        raise exception


@job('generate_analytics', timeout=3600)
def generate_analytics_dump(analytics_date, task_logger=None):
    local_time = as_local_datetime(timezone.now())
    task_logger = task_logger or CsvAnalyticsGeneratorTask(created_at=local_time)

    for api in KongApi.objects.all():
        csv_generator = AnalyticsCsvGenerator(api_name=api.name, analytics_date=analytics_date)
        generate_csv(csv_generator, task_logger, api.name, analytics_date)


@job('generate_indicators_csv', timeout=-1)  # no timeout
def generate_indicators_csv(force, task_logger=None):
    local_time = as_local_datetime(timezone.now())
    task_logger = task_logger or IndicatorCsvGeneratorTask(created_at=local_time)

    for api in KongApi.objects.all():
        IndicatorMetricsCalculator(api.name).calculate(force)
        csv_generator = IndicatorCsvGenerator(api_name=api.name)
        generate_csv(csv_generator, task_logger, api.name, None)


def perform_compression(force, api_name, task_logger, local_time):
    csv_compressor = CsvCompressor(api_name)
    try:
        if force:
            csv_compressor.compress_all()
        else:
            csv_compressor.compress_single_file(CsvFile.objects.last())
        task_logger.log_success(api_name, local_time)
    except Exception as exception:
        task_logger.log_error(api_name, local_time, exception)
        raise exception


@job('compress_csv_files', timeout=3600)
def compress_csv_files(force, task_logger=None):
    local_time = as_local_datetime(timezone.now())
    task_logger = task_logger or CsvCompressorTask(created_at=local_time)

    for api in KongApi.objects.all():
        perform_compression(force, api.name, task_logger, local_time)
