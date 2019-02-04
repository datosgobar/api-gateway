import datetime

import pytest
from mock import patch, Mock

from api_management.apps.analytics.csv_analytics.csv_compressor_and_remover \
    import CsvCompressorAndRemover
from api_management.apps.analytics.exceptions.invalid_csv_file import InvalidCsvFile
from api_management.apps.analytics.models import CsvFile
from api_management.apps.analytics.repositories.csv_file_repository import CsvFileRepository


def get_csv_file():
    return CsvFile(api_name='series',
                   type='analytics',
                   file_name='analytics_2018-12-20.csv',
                   file=Mock())


def test_time_from_csv_exception():
    with patch.object(CsvFileRepository, 'get_first', return_value=None):
        csv_remover = CsvCompressorAndRemover('series')

        with pytest.raises(InvalidCsvFile):
            csv_remover.time_from_first_csv_file()


def test_time_from_first_csv_file():
    with patch.object(CsvFileRepository, 'get_first', return_value=get_csv_file()):
        csv_remover = CsvCompressorAndRemover('series')

        assert csv_remover.time_from_first_csv_file() == datetime.datetime(2018, 12, 20)


def test_delete_files_out_range():
    with patch.object(CsvFileRepository, 'get_first', return_value=get_csv_file()):
        csv_remover = CsvCompressorAndRemover('series')

        date_1 = datetime.date(2018, 12, 20)
        date_2 = datetime.date.today()
        delta = date_2 - date_1

        with patch.object(CsvFileRepository, 'delete') as delete_call:
            csv_remover.delete_zipped_files(delta.days+1)
            delete_call.assert_not_called()


def test_delete_zipped_files():
    with patch.object(CsvFileRepository, 'get_first', return_value=get_csv_file()):
        with patch.object(CsvFileRepository, 'get_by_file_name', return_value=get_csv_file()):
            csv_remover = CsvCompressorAndRemover('series')

            with patch.object(CsvFileRepository, 'delete') as delete_call:
                csv_remover.delete_zipped_files(10)
                delete_call.assert_called()
