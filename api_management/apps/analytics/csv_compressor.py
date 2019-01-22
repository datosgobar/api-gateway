import zipfile

from django.conf import settings
from django.core.files import File
from django.utils import timezone

from api_management.apps.analytics.models import CsvFile, ZipFile


class CsvCompressor:

    def __init__(self, api_name):
        self.api_name = api_name

    def zip_name(self, year):
        return "analytics_{year}".format(year=year)

    def full_zip_name(self, file_name):
        return "{path}/{name}.zip".format(path=settings.MEDIA_ROOT, name=file_name)

    def first_csv_year(self):
        return int(CsvFile.objects.first().file_name[10:-10])

    def csv_range_years(self):
        return range(self.first_csv_year(), timezone.now().year + 1)

    def compress(self):
        for year in self.csv_range_years():
            files = CsvFile.objects.filter(type='analytics',
                                           api_name=self.api_name,
                                           file_name__icontains=year)
            self.perform_compression(files, self.zip_name(year))
            # self.delete_zipped_files(files)

    def perform_compression(self, csv_files, zip_name):
        zip_file_name = self.full_zip_name(zip_name)
        zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)

        for csv_file in csv_files:
            zip_file.write(csv_file.file.path, arcname=csv_file.file_name)

        zip_file.close()
        ZipFile(file_name=zip_file_name, file=File(zip_file)).save()
