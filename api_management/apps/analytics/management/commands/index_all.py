from django.core.management import BaseCommand

from api_management.apps.analytics.tasks import index_all


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Encolando proceso de indexación...")
        index_all.delay()
        self.stdout.write("Proceso encolado.")
