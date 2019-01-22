import zipfile

from dateutil import relativedelta
from django.conf import settings
from django.core.files import File
from django.utils import timezone

from api_management.apps.analytics.models import CsvFile, ZipFile


class CsvCompressor:

    def __init__(self, api_name):
        self.api_name = api_name

    def zip_name(self):
        return (timezone.now() - relativedelta.relativedelta(years=1)).strftime('analytics_%Y')

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
        self.perform_compression(files, self.zip_name())
        # files.delete()

    def perform_compression(self, csv_files, zip_name):
        zip_file_name = "{path}/{name}.zip".format(path=settings.MEDIA_ROOT, name=zip_name)
        zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)

        for csv_file in csv_files:
            zip_file.write(csv_file.file.path)

        zip_file.close()
        ZipFile(file_name=zip_file_name, file=File(zip_file)).save()
