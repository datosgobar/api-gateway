from django.core.management import BaseCommand

from api_management.apps.elastic_search.tasks import index_all


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Encolando indexación completa de objeto Query...")
        index_all.delay()
        self.stdout.write("Proceso encolado.")
