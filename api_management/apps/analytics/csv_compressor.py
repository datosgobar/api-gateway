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

    def year_from_csv_file(self, csv_file):
        return csv_file.file_name[10:-10]

    def first_csv_year(self):
        return int(self.year_from_csv_file(CsvFile.objects.first()))

    def csv_range_years(self):
        return range(self.first_csv_year(), timezone.now().year + 1)

    def compress_single_file(self, csv_file):
        year = self.year_from_csv_file(csv_file)
        zip_file = ZipFile.objects.filter(file_name__contains=str(year)).first()
        if zip_file is not None:
            opened_zip_file = zipfile.ZipFile(zip_file.file_name, 'w', zipfile.ZIP_DEFLATED)
            self.write_zip(opened_zip_file, csv_file)
            opened_zip_file.close()

    def compress_all(self):
        for year in self.csv_range_years():
            files = CsvFile.objects.filter(type='analytics',
                                           api_name=self.api_name,
                                           file_name__icontains=year)
            self.perform_compression(files, self.zip_name(year))

    def perform_compression(self, csv_files, zip_name):
        zip_file_name = self.full_zip_name(zip_name)
        zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)

        for csv_file in csv_files:
            self.write_zip(zip_file, csv_file)

        zip_file.close()
        ZipFile(file_name=zip_file_name, file=File(zip_file)).save()

    def write_zip(self, zip_file, csv_file):
        zip_file.write(csv_file.file.path, arcname=csv_file.file_name)
