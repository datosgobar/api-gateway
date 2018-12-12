import abc
import csv
from datetime import date

from dateutil import relativedelta
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from api_management.apps.analytics.models import Query, CsvFile, generate_api_session_id


def get_csv_writer(file):
    return csv.writer(file, quoting=csv.QUOTE_ALL)


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

    def generate(self):
        with NamedTemporaryFile(mode='r+', dir=settings.MEDIA_ROOT, suffix='.csv') as file:
            writer = get_csv_writer(file)
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

    def csv_file_type(self):
        return "analytics"

    def csv_filename(self):
        return "analytics_{date}.csv".format(date=self.date.date())

    def get_csv_file(self, file_name):
        return CsvFile.objects.filter(api_name=self.api_name,
                                      file_name=file_name,
                                      type="analytics").first()

    def write_content(self, writer, row_titles):
        for query in self.all_queries():
            attributes = [getattr(query, field, None) for field in row_titles]
            writer.writerow(attributes)

    def all_queries(self):
        min_date = self.date
        max_date = min_date + relativedelta.relativedelta(days=1)

        return Query.objects.filter(api_data__name=self.api_name,
                                    start_time__gte=min_date,
                                    start_time__lt=max_date).exclude(request_method='OPTIONS')


def is_mobile(user_agent):
    return "Mobile" in user_agent or \
           "Android" in user_agent or \
           "iPhone" in user_agent or \
           "Slackbot" in user_agent


def next_day_of(a_day):
    return a_day + relativedelta.relativedelta(days=1)


def indicator_row_content(queries):
    unique_session_ids = []
    total_mobile = 0
    total_not_mobile = 0

    for query in queries:
        session_id = generate_api_session_id(query)
        if session_id not in unique_session_ids:
            unique_session_ids.append(session_id)

        if is_mobile(query.user_agent):
            total_mobile = total_mobile + 1
        else:
            total_not_mobile = total_not_mobile + 1

    return {'total': total_mobile + total_not_mobile,
            'total_mobile': total_mobile,
            'total_not_mobile': total_not_mobile,
            'total_unique_users': len(unique_session_ids)}


class IndicatorCsvGenerator(AbstractCsvGenerator):

    def __init__(self, api_name):
        super().__init__(api_name=api_name)

    def row_titles(self):
        return ["indice_tiempo", "consultas_total", "consultas_dispositivos_moviles",
                "consultas_dispositivos_no_moviles", "usuarios_total"]

    def csv_file_type(self):
        return "indicators"

    def csv_filename(self):
        return "{name}-indicadores.csv".format(name=self.api_name)

    def get_csv_file(self, file_name):
        return CsvFile.objects.filter(api_name=self.api_name,
                                      file_name=file_name,
                                      type="indicators").first()

    def write_content(self, writer, _row_titles):
        query_time = Query.objects.first().start_time

        while query_time.date() < date.today():
            row = []
            queries = self.all_queries(query_time)
            total_counts = indicator_row_content(queries)

            row.append(query_time.date())
            row.append(total_counts.get('total'))
            row.append(total_counts.get('total_mobile'))
            row.append(total_counts.get('total_not_mobile'))
            row.append(total_counts.get('total_unique_users'))
            writer.writerow(row)

            query_time = next_day_of(query_time)

    def all_queries(self, query_time):
        return Query.objects.filter(api_data__name=self.api_name,
                                    start_time__gte=query_time,
                                    start_time__lt=next_day_of(query_time))\
                            .exclude(request_method='OPTIONS')
