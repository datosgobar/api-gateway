from django.core.management import BaseCommand
from django.utils import timezone

from api_management.apps.analytics.models import CsvCompressorTask
from api_management.apps.analytics.tasks import compress_csv_files


class Command(BaseCommand):

    def handle(self, *args, **options):
        force = options.get('all')
        self.compress_csv_files(force)

    def add_arguments(self, parser):
        parser.add_argument('--all', default=False, action='store_true')

    def compress_csv_files(self, force):
        task = CsvCompressorTask(created_at=timezone.now())
        self.stdout.write("Comprimiendo archivos csv...")
        compress_csv_files.delay(force, task)
        self.stdout.write("Proceso encolado.")
