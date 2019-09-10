import argparse
import datetime

import dateutil
from django.utils import timezone
from django.core.management import BaseCommand
from api_management.apps.analytics.models import Query


def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):
    help = '''
    Borra todos los registros de queries asociados a dirección IP y a una fecha (YYYY-MM-DD)
    '''

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='Dirección IP sobre la cual borrar registros')
        parser.add_argument('date', type=valid_date, help='Fecha YYYY-MM-DD sobre la cual borrar registros')
        parser.add_argument('--confirm', default=False, action='store_true')

    def handle(self, *args, **options):
        ip_address = options['ip_address']
        query_datetime = self.parse_datetime(options)
        day_after = query_datetime + dateutil.relativedelta.relativedelta(days=1)
        queries = Query.objects.filter(ip_address=ip_address,
                                       start_time__lt=day_after,
                                       start_time__gte=query_datetime)
        self.stdout.write(f'Se van a borrar {queries.count()} queries, '
                          f'de la dirección {ip_address}, fecha {query_datetime.date()}')

        if not options['confirm']:
            resp = input('Confirmar [y/N]: ')
            if resp.lower() != 'y':
                self.stdout.write('Abortando')
                return

        queries.delete()
        self.stdout.write("Queries borradas")

    def parse_datetime(self, options):
        query_date = options['date']
        query_datetime = timezone.make_aware(datetime.datetime.combine(query_date, datetime.time()))
        return query_datetime
