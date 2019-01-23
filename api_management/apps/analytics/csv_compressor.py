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

    def years_from_csv_file_name(self, csv_file):
        return csv_file.file_name[10:-10]

    def year_of_first_csv_file(self):
        return int(self.years_from_csv_file_name(CsvFile.objects.first()))

    def csv_range_years(self):
        return range(self.year_of_first_csv_file(), timezone.now().year + 1)

    def open_zip(self, file_name):
        return zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)

    def get_or_initialize_zip_file(self, csv_file):
        year = self.years_from_csv_file_name(csv_file)
        zip_file = ZipFile.objects.filter(file_name__contains=str(year)).first()

        return zip_file or ZipFile(file_name=self.full_zip_name(self.zip_name(year)))

    def compress_single_file(self, csv_file):
        zip_file = self.get_or_initialize_zip_file(csv_file)
        open_file = self.open_zip(zip_file.file_name)
        self.write_zip(open_file, csv_file)
        open_file.close()
        zip_file.file = File(open_file)
        zip_file.save()

    def compress_all(self):
        for year in self.csv_range_years():
            files = CsvFile.objects.filter(type='analytics',
                                           api_name=self.api_name,
                                           file_name__icontains=year)
            self.perform_compression(files, self.zip_name(year))

    def perform_compression(self, csv_files, zip_name):
        zip_file_name = self.full_zip_name(zip_name)
        zip_file = self.open_zip(zip_file_name)

        for csv_file in csv_files:
            self.write_zip(zip_file, csv_file)

        zip_file.close()
        ZipFile.objects.update_or_create(file_name=zip_file_name, file=File(zip_file))

    def write_zip(self, zip_file, csv_file):
        zip_file.write(csv_file.file.path, arcname=csv_file.file_name)
