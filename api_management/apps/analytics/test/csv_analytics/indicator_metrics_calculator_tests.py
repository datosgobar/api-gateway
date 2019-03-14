from datetime import datetime
from unittest.mock import patch

import pytest

from api_management.apps.analytics.csv_analytics.csv_generator import IndicatorCsvGenerator

MODULE_PATH = 'api_management.apps.analytics.csv_analytics.csv_generator.IndicatorCsvGenerator'


@pytest.mark.django_db
def test_historic_hits_default(empty_historic_hits):
    csv_generator = IndicatorCsvGenerator(api_name='series')

    with patch(MODULE_PATH + '.historic_hit_by_api', return_value=empty_historic_hits):
        with patch(MODULE_PATH + '.total_queries_by_date', return_value=50):

            assert csv_generator.total_historic_hits(datetime(2018, 10, 10)) == 50


@pytest.mark.django_db
def test_historic_hits_with_data(historic_hits):
    csv_generator = IndicatorCsvGenerator(api_name='series')

    with patch(MODULE_PATH + '.historic_hit_by_api', return_value=historic_hits):
        with patch(MODULE_PATH + '.total_queries_by_date', return_value=50):

            assert historic_hits.accumulated_hits == 100
            assert csv_generator.total_historic_hits(datetime(2018, 10, 10)) == 150
