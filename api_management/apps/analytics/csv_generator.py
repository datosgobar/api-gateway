import csv

from dateutil import relativedelta
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from api_management.apps.analytics.models import Query, CsvFile


class CsvGenerator:

    def __init__(self, api_name, date):
        self.api_name = api_name
        self.date = date

    def generate(self):
        file_name = "analytics_{date}.csv".format(date=self.date.date())

        with NamedTemporaryFile(mode='r+', dir=settings.MEDIA_ROOT, suffix='.csv') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            field_names = [field.name for field in Query._meta.get_fields()]
            writer.writerow(field_names)
            for query in self.all_queries():
                attributes = [getattr(query, str(field), None) for field in field_names]
                writer.writerow(attributes)

            self.create_csv_file(file_name, file)

    def all_queries(self):
        min_date = self.date
        max_date = min_date + relativedelta.relativedelta(days=1)

        return Query.objects.filter(api_data__name=self.api_name,
                                    start_time__gte=min_date,
                                    start_time__lt=max_date)

    def create_csv_file(self, file_name, file):
        csv_file = CsvFile.objects.filter(api_name=self.api_name, file_name=file_name).first()
        if csv_file is not None:
            if csv_file.file.name != '':
                csv_file.file.delete()  # removes from disk
            csv_file.file = File(file)
            csv_file.save()
        else:
            CsvFile(api_name=self.api_name, file_name=file_name, file=File(file)).save()
