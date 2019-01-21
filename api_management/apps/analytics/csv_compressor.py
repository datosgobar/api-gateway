import zipfile

from dateutil import relativedelta
from django.utils import timezone

from api_management.apps.analytics.models import CsvFile, ZipFile


class CsvCompressor:

    def __init__(self, api_name):
        self.api_name = api_name

    def last_year_file_names(self):
        date_list = [timezone.now() - relativedelta.relativedelta(days=x) for x in range(0, 365)]
        date_strings = map(lambda x: x.strftime('%Y-%m-%d'), date_list)
        return list(map(lambda x: "analytics_{date}.csv".format(date=x), date_strings))

    def older_than_last_year(self):
        file_names = self.last_year_file_names()
        return CsvFile.objects.filter(type='analytics',
                                      api_name=self.api_name).exclude(file_name__in=file_names)

    def compress(self):
        files = self.older_than_last_year()
        self.perform_compression(files)
        files.delete()

    def perform_compression(self, csv_files):
        for csv_file in csv_files:
            zip_file_name = "{name}.zip".format(name=csv_file.file_name[:-3])
            zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
            zip_file.write(csv_file.file.path, arcname=zip_file_name)
            zip_file.close()
            ZipFile(name=zip_file_name, file=zip_file).save()
