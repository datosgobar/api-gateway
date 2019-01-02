from dateutil import relativedelta
from django.core.management import BaseCommand
from django.utils import timezone

from api_management.apps.analytics.models import Query, IndicatorCsvGeneratorTask
from api_management.apps.analytics.tasks import generate_indicators_csv


def yesterday():
    return timezone.now() - relativedelta.relativedelta(days=1)


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not Query.objects.count():
            self.stdout.write("No hay queries cargadas.")
            return

        if options.get('all'):
            self.generate_indicators_csv(force=True)
        else:
            self.generate_indicators_csv(force=False)

    def add_arguments(self, parser):
        parser.add_argument('--all', default=False, action='store_true')

    def generate_indicators_csv(self, force):
        task = IndicatorCsvGeneratorTask(created_at=timezone.now())
        self.stdout.write("Generando csv de indicadores...")
        generate_indicators_csv.delay(force, task)
        self.stdout.write("La generación terminó.")
