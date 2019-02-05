from unittest.mock import Mock

from api_management.apps.analytics.models import CsvFile


def test_years_from_name():
    csv_file = CsvFile(api_name='series',
                       type='analytics',
                       file_name='analytics_2018-12-20.csv',
                       file=Mock())

    assert csv_file.years_from_name() == '2018'


def test_date_from_name():
    csv_file = CsvFile(api_name='series',
                       type='analytics',
                       file_name='analytics_2018-12-20.csv',
                       file=Mock())

    assert csv_file.date_from_name().strftime('%Y-%m-%d') == '2018-12-20'
