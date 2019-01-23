import os
from unittest import mock

import pytest
from django.conf import settings
from django.core.files import File
from django.utils import timezone

from api_management.apps.analytics.csv_compressor import CsvCompressor
from api_management.apps.analytics.models import CsvFile, ZipFile


def csv_compressor():
    return CsvCompressor('series')


def get_file_mock(file_name):
    file_mock = mock.MagicMock(spec=File, name='FileMock')
    file_mock.name = str(settings.MEDIA_ROOT + '/' + file_name)
    return file_mock


def test_zip_name():
    assert csv_compressor().zip_name(2018) == 'analytics_2018'
    assert csv_compressor().zip_name('2018') == 'analytics_2018'


def test_full_zip_name():
    full_name = "{path}/analytics_2018.zip".format(path=settings.MEDIA_ROOT)
    assert csv_compressor().full_zip_name('analytics_2018') == full_name


def test_years_from_csv_file_name():
    csv_file = CsvFile(api_name='series', file_name='analytics_2017-10-15.csv')
    assert csv_compressor().years_from_csv_file_name(csv_file) == '2017'


@pytest.mark.django_db
def test_year_of_first_csv_file():
    CsvFile(api_name='series', file_name='analytics_2017-10-15.csv').save()
    CsvFile(api_name='series', file_name='analytics_2017-11-25.csv').save()
    CsvFile(api_name='series', file_name='analytics_2018-10-15.csv').save()

    assert csv_compressor().year_of_first_csv_file() == 2017


@pytest.mark.django_db
def test_csv_range_years():
    current_year = timezone.now().year
    CsvFile(api_name='series', file_name='analytics_2017-10-15.csv').save()
    CsvFile(api_name='series', file_name='analytics_2017-11-25.csv').save()
    CsvFile(api_name='series', file_name='analytics_2018-10-15.csv').save()

    assert csv_compressor().csv_range_years() == range(2017, current_year + 1)


@pytest.mark.django_db
def test_compress_single_file():
    file_name = 'analytics_2018-08-15.csv'
    csv_file = CsvFile(api_name='series', file_name=file_name, file=get_file_mock(file_name))

    zip_file_count = ZipFile.objects.count()
    csv_compressor().compress_single_file(csv_file)

    assert ZipFile.objects.count() == zip_file_count + 1
    assert 'analytics_2018.zip' in ZipFile.objects.first().file_name

    os.remove(ZipFile.objects.first().file_name)
