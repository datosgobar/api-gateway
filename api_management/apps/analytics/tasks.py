from django.utils import timezone
from django_rq import job

from api_management.apps.analytics.csv_generator import AnalyticsCsvGenerator, \
    IndicatorCsvGenerator
from api_management.apps.analytics.models import CsvAnalyticsGeneratorTask, \
    IndicatorCsvGeneratorTask
from api_management.apps.api_registry.models import KongApi


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
    task_logger = task_logger or CsvAnalyticsGeneratorTask(created_at=timezone.now())

    for api in KongApi.objects.all():
        csv_generator = AnalyticsCsvGenerator(api_name=api.name, analytics_date=analytics_date)
        generate_csv(csv_generator, task_logger, api.name, analytics_date)


@job('generate_indicators_csv', timeout=3600)
def generate_indicators_csv(task_logger=None):
    task_logger = task_logger or IndicatorCsvGeneratorTask(created_at=timezone.now())

    for api in KongApi.objects.all():
        csv_generator = IndicatorCsvGenerator(api_name=api.name)
        generate_csv(csv_generator, task_logger, api.name, None)
