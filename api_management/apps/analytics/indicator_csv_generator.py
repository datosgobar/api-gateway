import csv
from datetime import date

from dateutil import relativedelta
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile

from api_management.apps.analytics.models import Query


def is_mobile(user_agent):
    return "Mobile" in user_agent or \
           "Android" in user_agent or \
           "iPhone" in user_agent or \
           "Slackbot" in user_agent


def next_day_of(a_day):
    return a_day + relativedelta.relativedelta(days=1)


def indicators_csv_titles():
    return ["indice_tiempo", "consultas_total", "consultas_dispositivos_moviles",
            "consultas_dispositivos_no_moviles", "usuarios_total"]


def get_mobile_count(queries):
    total = 0
    for query in queries:
        if is_mobile(query.user_agent):
            total = total + 1
    return total


def get_not_mobile_count(queries):
    total = 0
    for query in queries:
        if not is_mobile(query.user_agent):
            total = total + 1
    return total


def get_unique_users_count(_queries):
    return 0


class IndicatorCsvGenerator:

    def __init__(self, api_name):
        self.api_name = api_name

    def generate(self):
        file_name = "{name}-indicator.csv".format(name=self.api_name)

        with NamedTemporaryFile(mode='r+', dir=settings.MEDIA_ROOT, suffix='.csv') as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            titles = indicators_csv_titles()

            writer.writerow(titles)

            from_time = Query.objects.first().start_time
            to_time = next_day_of(from_time)

            while to_time < date.today():
                row = []
                queries = self.all_queries(from_time, to_time)

                row.append("indice de tiempo")
                row.append(queries.count())
                row.append(get_mobile_count(queries))
                row.append(get_not_mobile_count(queries))
                row.append(get_unique_users_count(queries))

                to_time = next_day_of(to_time)

            self.create_csv_file(file_name, file)

    def all_queries(self, from_time, to_time):
        return Query.objects.filter(api_data__name=self.api_name,
                                    start_time__gte=from_time,
                                    start_time__lt=to_time).exclude(request_method='OPTIONS')

    def create_csv_file(self, file_name, file):
        pass
        # TODO: Completar. No repetir código con CsvGenerator
