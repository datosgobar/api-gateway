import csv

from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from api_management.apps.analytics.models import Query, CsvFile


class CsvGenerator:  # pylint: disable=too-few-public-methods

    def __init__(self, api_name, date):
        self.api_name = api_name
        self.date = date

    def generate(self):
        file_name = f'analytics_{self.date.date()}.csv'

        with NamedTemporaryFile(mode='r+', dir=settings.MEDIA_ROOT, suffix='.csv') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            field_names = [field.name for field in Query._meta.get_fields()]
            writer.writerow(field_names)
            for query in Query.objects.filter(uri=self.api_name, start_time=self.date):
                attributes = [getattr(query, str(field), None) for field in field_names]
                writer.writerow(attributes)

            CsvFile.objects.update_or_create(api_name=self.api_name,
                                             file_name=file_name,
                                             defaults={"file": File(file)})
