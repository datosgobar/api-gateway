import datetime

from dateutil import relativedelta
from django.core.management import BaseCommand
from django.utils import timezone

from api_management.apps.analytics.models import Query, CsvAnalyticsGeneratorTask, next_day_of
from api_management.apps.analytics.tasks import generate_analytics_dump
from api_management.apps.common.utils import date_at_midnight


def yesterday():
    return date_at_midnight(timezone.now()) - relativedelta.relativedelta(days=1)


class Command(BaseCommand):

    def handle(self, *args, **options):
        if options.get('all'):
            first_query = Query.objects.all().order_by("start_time").first()
            if first_query is None:
                self.stdout.write("No hay queries cargadas.")
                return

            self.generate_all_analytics(date_at_midnight(first_query.start_time), yesterday())
        if options.get('date'):
            self.generate_analytics_by(options.get('date'))
        else:
            self.generate_analytics_once()

    def add_arguments(self, parser):
        parser.add_argument('--all', default=False, action='store_true')
        parser.add_argument('--date')

    def generate_analytics_by(self, a_date):
        from_time = datetime.datetime.strptime(a_date, "%Y-%m-%d")
        from_time.replace(hour=0, minute=0)
        to_time = from_time.replace(hour=23, minute=59)
        query = Query.objects.filter(start_time__gte=from_time, start_time__lte=to_time).first()
        if query is not None:
            self.generate_all_analytics(query.start_time, next_day_of(query.start_time))
        else:
            self.stdout.write("No hay queries para ese día.")

    def generate_all_analytics(self, from_time, to_time):
        next_date = from_time
        task = CsvAnalyticsGeneratorTask(created_at=timezone.now())
        while next_date < to_time:
            self.generate_analytics(task, next_date)
            next_date = next_date + relativedelta.relativedelta(days=1)

    def generate_analytics_once(self):
        task = CsvAnalyticsGeneratorTask(created_at=timezone.now())
        self.generate_analytics(task, yesterday())

    def generate_analytics(self, task, analytics_date):
        self.stdout.write("Generando csv para el día {date}...".format(date=analytics_date.date()))
        generate_analytics_dump.delay(analytics_date, task)
