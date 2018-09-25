from django_rq import job
from datetime import timedelta
from api_management.apps.analytics.csv_generator import CsvGenerator
from api_management.apps.api_registry.models import KongApi


@job('create_model')
def make_model_object(data, serializer_class):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()


@job('generate_analytics')
def generate_analytics_dump(date=None):
    if date is None:
        date = (date.today() - timedelta(1)).strftime('%Y-%m-%d')

    for api in KongApi.objects.all():
        csv_generator = CsvGenerator(api_name=api.name, date=date)
        csv_generator.generate()
