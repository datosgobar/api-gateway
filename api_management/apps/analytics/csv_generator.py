import abc
import csv

from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from api_management.apps.analytics.models import Query, CsvFile, IndicatorMetricsRow, next_day_of


class AbstractCsvGenerator:

    def __init__(self, api_name):
        self.api_name = api_name

    @abc.abstractmethod
    def row_titles(self):
        raise NotImplementedError

    @abc.abstractmethod
    def write_content(self, _writer, _row_titles):
        raise NotImplementedError

    @abc.abstractmethod
    def csv_filename(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_csv_file(self, file_name):
        raise NotImplementedError

    @abc.abstractmethod
    def csv_file_type(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_csv_writer(self, file):
        raise NotImplementedError

    def generate(self):
        with NamedTemporaryFile(mode='r+', dir=settings.MEDIA_ROOT, suffix='.csv') as file:
            writer = self.get_csv_writer(file)
            csv_header = self.row_titles()
            writer.writerow(csv_header)
            self.write_content(writer, csv_header)
            self.create_csv_file(self.csv_filename(), file)

    def create_csv_file(self, file_name, file):
        csv_file = self.get_csv_file(file_name)
        if csv_file is not None:
            if csv_file.file.name != '':
                csv_file.file.delete()  # removes from disk
            csv_file.file = File(file)
            csv_file.save()
        else:
            CsvFile(api_name=self.api_name,
                    file_name=file_name,
                    file=File(file),
                    type=self.csv_file_type()).save()


class AnalyticsCsvGenerator(AbstractCsvGenerator):

    def __init__(self, api_name, analytics_date):
        super().__init__(api_name=api_name)
        self.date = analytics_date

    def row_titles(self):
        return [field.name for field in Query._meta.get_fields()]

    def get_csv_writer(self, file):
        return csv.writer(file, quoting=csv.QUOTE_ALL)

    def csv_file_type(self):
        return CsvFile.TYPE_ANALYTICS

    def csv_filename(self):
        return "analytics_{date}.csv".format(date=self.date.date())

    def get_csv_file(self, file_name):
        return CsvFile.objects.filter(api_name=self.api_name,
                                      file_name=file_name,
                                      type=CsvFile.TYPE_ANALYTICS).first()

    def write_content(self, writer, row_titles):
        for query in self.all_queries():
            attributes = [getattr(query, field, None) for field in row_titles]
            writer.writerow(attributes)

    def all_queries(self):
        min_date = self.date
        max_date = next_day_of(min_date)

        return Query.objects.filter(api_data__name=self.api_name,
                                    start_time__gte=min_date,
                                    start_time__lt=max_date).exclude(request_method='OPTIONS')


class IndicatorCsvGenerator(AbstractCsvGenerator):

    def __init__(self, api_name):
        super().__init__(api_name=api_name)

    def row_titles(self):
        return ["indice_tiempo", "consultas_total", "consultas_dispositivos_moviles",
                "consultas_dispositivos_no_moviles", "usuarios_total"]

    def get_csv_writer(self, file):
        return csv.writer(file, quoting=csv.QUOTE_NONE)

    def csv_file_type(self):
        return CsvFile.TYPE_INDICATORS

    def csv_filename(self):
        return "{name}-indicadores.csv".format(name=self.api_name)

    def get_csv_file(self, file_name):
        return CsvFile.objects.filter(api_name=self.api_name,
                                      file_name=file_name,
                                      type=CsvFile.TYPE_INDICATORS).first()

    def write_content(self, writer, _row_titles):
        for metric_row in IndicatorMetricsRow.objects.filter(api_name=self.api_name):
            row = [metric_row.date,
                   metric_row.all_queries,
                   metric_row.all_mobile,
                   metric_row.all_not_mobile,
                   metric_row.total_users]
            writer.writerow(row)
