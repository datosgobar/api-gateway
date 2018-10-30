from django.utils import timezone
from django_rq import job

from api_management.apps.analytics.csv_generator import CsvGenerator
from api_management.apps.analytics.models import CsvAnalyticsGeneratorTask
from api_management.apps.api_registry.models import KongApi


@job('create_model')
def make_model_object(data, serializer_class):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()


@job('generate_analytics', timeout=3600)
def generate_analytics_dump(analytics_date, task_logger=None):
    task_logger = task_logger or CsvAnalyticsGeneratorTask(created_at=timezone.now())

    for api in KongApi.objects.all():
        csv_generator = CsvGenerator(api_name=api.name, date=analytics_date)
        try:
            csv_generator.generate()
            task_logger.log_success(api.name, analytics_date)
        except Exception as exception:
            task_logger.log_error(api.name, analytics_date, exception)
            raise exception
