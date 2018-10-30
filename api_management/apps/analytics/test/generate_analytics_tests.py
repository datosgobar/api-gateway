from unittest.mock import patch

import pytest
from dateutil import relativedelta
from django.utils import timezone

from api_management.apps.analytics.management.commands.generate_analytics import Command


@pytest.mark.django_db
def test_creates_csv_for_yesterday():
    task_command = Command()

    with patch('api_management.apps.analytics.management.commands.generate_analytics'
               '.Command.generate_analytics') as generate_analytics_call:
        task_command.generate_analytics_once()

        generate_analytics_call.assert_called_once()

        requested_time = generate_analytics_call.call_args[0][1].date()
        yesterday = (timezone.now() - relativedelta.relativedelta(days=1)).date()

        assert requested_time == yesterday


@pytest.mark.django_db
def test_creates_csv_for_a_range():
    task_command = Command()
    from_time = timezone.now() - relativedelta.relativedelta(days=3)
    to_time = timezone.now() - relativedelta.relativedelta(days=1)

    with patch('api_management.apps.analytics.management.commands.generate_analytics'
               '.Command.generate_all_analytics') as generate_all_analytics_call:
        task_command.generate_all_analytics(from_time, to_time)

        generate_all_analytics_call.assert_called_once_with(from_time, to_time)
