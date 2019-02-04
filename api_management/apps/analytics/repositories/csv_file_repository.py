from api_management.apps.analytics.models import CsvFile


class CsvFileRepository:

    def __init__(self, csv_type, api_name):
        self.csv_type = csv_type
        self.api_name = api_name

    def get_first(self):
        return CsvFile.objects.filter(api_name=self.api_name).first()

    def get_by_file_name(self, file_name):
        return CsvFile.objects.filter(api_name=self.api_name,
                                      file_name__contains=file_name)

    def delete(self, csv_file):
        if csv_file.file is not None:
            csv_file.file.delete()
        csv_file.delete()
