from dateutil import relativedelta
from django.core.management import BaseCommand
from django.utils import timezone

from api_management.apps.analytics.models import Query, CsvAnalyticsGeneratorTask
from api_management.apps.analytics.tasks import generate_analytics_dump


def yesterday():
    return timezone.now() - relativedelta.relativedelta(days=1)


def error_task_log(analytics_date, exception):
    return "Error generando csv de analytics para el día {value}: {exception}"\
        .format(value=analytics_date, exception=exception)


def success_task_log(analytics_date):
    return "Csv de analytics generado correctamente para el día {date}."\
        .format(date=analytics_date)


class Command(BaseCommand):

    def handle(self, *args, **options):
        if options.get('all'):
            first_query = Query.objects.all().order_by("start_time").first()
            if first_query is None:
                self.stdout.write("No hay queries cargadas.")
                return

            self.generate_all_analytics(first_query.start_time, yesterday())
        else:
            self.generate_analytics_once()

    def add_arguments(self, parser):
        parser.add_argument('--all', default=False, action='store_true')

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
        try:
            generate_analytics_dump.delay(analytics_date)
            task.logs += success_task_log(analytics_date)
            task.save()
        except Exception as e:
            task.logs += error_task_log(analytics_date, e)
            task.save()
            raise e
