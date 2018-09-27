from datetime import date

from dateutil import relativedelta
from django.core.management import BaseCommand

from api_management.apps.analytics.models import Query
from api_management.apps.analytics.tasks import generate_analytics_dump


class Command(BaseCommand):

    def handle(self, *args, **options):
        if options.get('all'):
            start_date = Query.objects.all().order_by("start_date").first()
            if start_date is None:
                self.stdout.write("No hay queries cargadas.")
                return

            next_date = start_date
            while next_date != date.today:
                generate_analytics_dump(next_date)
                next_date = next_date + relativedelta.relativedelta(days=1)
        else:
            generate_analytics_dump.delay()

    def add_arguments(self, parser):
        parser.add_argument('--all', default=False, action='store_true')
