from django.core.management import BaseCommand
from django.utils import timezone

from api_management.apps.analytics.models import CsvCompressorTask
from api_management.apps.analytics.tasks import compress_csv_files


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.compress_csv_files()

    def compress_csv_files(self):
        task = CsvCompressorTask(created_at=timezone.now())
        self.stdout.write("Comprimiendo archivos csv...")
        compress_csv_files.delay(task)
        self.stdout.write("Proceso encolado.")
