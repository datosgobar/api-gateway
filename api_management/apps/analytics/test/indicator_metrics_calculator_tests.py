from unittest.mock import patch

from datetime import datetime
import pytest

from api_management.apps.analytics.csv_generator import IndicatorCsvGenerator
from api_management.apps.analytics.metrics_calculator import IndicatorMetricsCalculator
from api_management.apps.analytics.models import Query
from api_management.apps.analytics.test.user_agents import user_agents
from api_management.apps.api_registry.models import KongApiHistoricHits


def test_is_mobile():
    calculator = IndicatorMetricsCalculator(api_name='foo')

    assert calculator.is_mobile(user_agents.get('linux')) is False
    assert calculator.is_mobile(user_agents.get('safari_ios'))
    assert calculator.is_mobile(user_agents.get('android_firefox'))
    assert calculator.is_mobile(user_agents.get('slack_browser'))


def test_indicator_row_content(kong_api):
    queries = [Query(ip_address="192.168.1.1", host="foo", uri="/series", querystring="?foo=1",
                     start_time=datetime.now(), request_time=1, status_code=200,
                     api_data=kong_api, user_agent=user_agents.get('safari_ios'), token="123",
                     request_method="POST")]

    calculator = IndicatorMetricsCalculator(api_name='foo')
    row_contents = calculator.indicator_row_content(queries)

    assert row_contents.get('total') == 1
    assert row_contents.get('total_mobile') == 1
    assert row_contents.get('total_not_mobile') == 0
    assert row_contents.get('total_unique_users') == 1


@pytest.mark.django_db
def test_historic_hits_default():
    queries = 50
    csv_generator = IndicatorCsvGenerator(api_name='foo')

    assert csv_generator.historic_hits(queries) == 50
    assert KongApiHistoricHits.objects.count() == 0


@pytest.mark.django_db
def test_historic_hits_with_data(historic_hits):
    queries = 50
    csv_generator = IndicatorCsvGenerator(api_name='series')

    with patch('api_management.apps.analytics.csv_generator.IndicatorCsvGenerator'
               '.historic_hit_by_api', return_value=historic_hits):

        assert historic_hits.accumulated_hits == 100
        assert csv_generator.historic_hits(queries) == 150
