from datetime import date
from dateutil import relativedelta
from django_rq import job

from api_management.apps.analytics.csv_generator import CsvGenerator
from api_management.apps.api_registry.models import KongApi


@job('create_model')
def make_model_object(data, serializer_class):
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()


@job('generate_analytics', timeout=3600)
def generate_analytics_dump(date_string=None):
    if date_string is None:
        date_string = date.today() - relativedelta.relativedelta(days=1)

    for api in KongApi.objects.all():
        csv_generator = CsvGenerator(api_name=api.name, date=date_string)
        csv_generator.generate()
