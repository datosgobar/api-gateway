import os
import zipfile

from django.conf import settings
from django.core.files import File
from django.utils import timezone

from api_management.apps.analytics.models import CsvFile, ZipFile
from api_management.apps.analytics.repositories.csv_file_repository import CsvFileRepository


class CsvCompressor:

    def __init__(self, api_name):
        self.api_name = api_name
        self.csv_file_repository = CsvFileRepository('analytics', self.api_name)

    def path_to_file(self, file_name):
        return "{path}/{file_name}".format(path=settings.MEDIA_ROOT, file_name=file_name)

    def zip_name(self, year):
        return "analytics_{year}.zip".format(year=year)

    def years_from_csv_file_name(self, csv_file):
        return csv_file.file_name[10:14]

    def year_of_first_csv_file(self):
        return int(self.years_from_csv_file_name(self.csv_file_repository.get_first()))

    def csv_range_years(self):
        return range(self.year_of_first_csv_file(), timezone.now().year + 1)

    def open_zip(self, file_name):
        return zipfile.ZipFile(file_name, 'a', zipfile.ZIP_DEFLATED)

    def get_or_initialize_zip_file(self, csv_file):
        year = self.years_from_csv_file_name(csv_file)
        zip_file = ZipFile.objects.filter(api_name=self.api_name,
                                          file_name__contains=str(year)).first()

        return zip_file or ZipFile(api_name=self.api_name, file_name=self.zip_name(year))

    def compress_single_file(self, csv_file):
        zip_file = self.get_or_initialize_zip_file(csv_file)
        open_file = self.open_zip(self.path_to_file(zip_file.file_name))
        self.write_zip(open_file, csv_file)
        open_file.close()
        with open(self.path_to_file(zip_file.file_name), 'rb') as file_to_save:
            zip_file.file = File(file_to_save)
            zip_file.save()
            # remove zip created with zipfile.ZipFile
            os.remove(self.path_to_file(zip_file.file_name))

    def compress_all(self):
        for year in self.csv_range_years():
            files = CsvFile.objects.filter(type='analytics',
                                           api_name=self.api_name,
                                           file_name__icontains=year)
            self.perform_compression(files, self.zip_name(year))

    def perform_compression(self, csv_files, zip_name):
        open_file = self.open_zip(self.path_to_file(zip_name))

        for csv_file in csv_files:
            self.write_zip(open_file, csv_file)

        open_file.close()
        with open(self.path_to_file(zip_name), 'rb') as file_to_save:
            ZipFile.objects.update_or_create(api_name=self.api_name,
                                             file_name=zip_name,
                                             defaults={'file': File(file_to_save)})
            os.remove(self.path_to_file(zip_name))  # remove zip created with zipfile.ZipFile

    def can_write_zip(self, csv_file, zipped_files):
        return csv_file.file.storage.exists(csv_file.file.path) \
                    and all(name != csv_file.file_name for name in zipped_files)

    def write_zip(self, zip_file, csv_file):
        if not zip_file.namelist():
            zip_file.write(csv_file.file.path, csv_file.file_name)
        else:
            if self.can_write_zip(csv_file, zip_file.namelist()):
                zip_file.write(csv_file.file.path, csv_file.file_name)
