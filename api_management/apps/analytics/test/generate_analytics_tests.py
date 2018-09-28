import pytest
from dateutil import relativedelta
from django.utils import timezone

from api_management.apps.analytics.management.commands.generate_analytics import Command
from api_management.apps.analytics.models import CsvFile, CsvAnalyticsGeneratorTask


@pytest.mark.django_db
def test_creates_csv_for_yesterday():
    task_command = Command()
    csv_count = CsvFile.objects.count()

    task_command.generate_analytics_once()
    assert csv_count + 1, CsvFile.objects.count()
    assert CsvAnalyticsGeneratorTask.objects.first().logs, \
        "Archivo csv de analytics generado correctamente."


@pytest.mark.django_db
def test_creates_csv_for_a_range():
    task_command = Command()
    from_time = timezone.now() - relativedelta.relativedelta(days=3)
    to_time = timezone.now() - relativedelta.relativedelta(days=1)
    csv_count = CsvFile.objects.count()

    task_command.generate_all_analytics(from_time, to_time)
    assert (csv_count + 2), CsvFile.objects.count()


@pytest.mark.django_db
def test_skip_today():
    task_command = Command()
    from_time = timezone.now() - relativedelta.relativedelta(days=1)
    to_time = timezone.now()
    csv_count = CsvFile.objects.count()

    task_command.generate_all_analytics(from_time, to_time)
    assert (csv_count + 1), CsvFile.objects.count()
