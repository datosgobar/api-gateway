from dateutil import relativedelta
from django.core.management import BaseCommand
from django.utils import timezone

from api_management.apps.analytics.models import Query, CsvAnalyticsGeneratorTask
from api_management.apps.analytics.tasks import generate_analytics_dump


class Command(BaseCommand):

    def handle(self, *args, **options):
        if options.get('all'):
            first_query = Query.objects.all().order_by("start_time").first()
            if first_query is None:
                self.stdout.write("No hay queries cargadas.")
                return

            next_date = first_query.start_time
            while next_date < timezone.now():
                self.stdout.write(f"Generando csv para el día {next_date.date()}...")
                generate_analytics_dump(next_date)
                next_date = next_date + relativedelta.relativedelta(days=1)
        else:
            task = CsvAnalyticsGeneratorTask(date=timezone.now())
            try:
                generate_analytics_dump.delay()
                task.logs += "Archivo csv de analytics generado correctamente."
                task.save()
            except Exception as e:
                task.logs += f"Error generando csv de analytics: {e}"
                task.save()
                raise e

    def add_arguments(self, parser):
        parser.add_argument('--all', default=False, action='store_true')
