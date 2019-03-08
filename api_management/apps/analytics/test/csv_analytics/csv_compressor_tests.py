import os
from unittest import mock

import pytest
from django.conf import settings
from django.core.files import File
from django.utils import timezone

from api_management.apps.analytics.csv_analytics.csv_compressor import CsvCompressor
from api_management.apps.analytics.models import CsvFile, ZipFile


def csv_compressor():
    return CsvCompressor('series')


def get_file_mock(file_name):
    file_mock = mock.MagicMock(spec=File, name='FileMock')
    file_mock.name = str(settings.MEDIA_ROOT + file_name)
    return file_mock


def create_csv_file(name):
    with open(str(settings.MEDIA_ROOT + name), 'r+') as file:
        CsvFile(type='analytics', api_name='series', file_name=name, file=File(file)).save()
        return file


@pytest.mark.django_db
def delete_files():
    for csv_file in CsvFile.objects.all():
        os.remove(csv_file.file.path)

    for zip_file in ZipFile.objects.all():
        os.remove(zip_file.file.name)


@pytest.fixture(autouse=True)
def fixture_func():
    yield
    delete_files()


@pytest.mark.django_db
def test_zip_name():
    assert csv_compressor().zip_name(2018) == 'analytics_2018.zip'
    assert csv_compressor().zip_name('2018') == 'analytics_2018.zip'


@pytest.mark.django_db
def test_path_to_file():
    full_name = "{path}/analytics_2018.zip".format(path=settings.MEDIA_ROOT)
    assert csv_compressor().path_to_file('analytics_2018.zip') == full_name


@pytest.mark.django_db
def test_years_from_csv_file_name():
    csv_file = CsvFile(api_name='series', file_name='analytics_2017-10-15.csv')
    assert csv_compressor().years_from_csv_file_name(csv_file) == '2017'


@pytest.mark.django_db
def test_year_of_first_csv_file():
    create_csv_file('analytics_2017-10-15.csv')
    create_csv_file('analytics_2017-11-25.csv')
    create_csv_file('analytics_2018-10-15.csv')

    assert csv_compressor().year_of_first_csv_file() == 2017


@pytest.mark.django_db
def test_csv_range_years():
    current_year = timezone.now().year
    create_csv_file('analytics_2017-10-15.csv')
    create_csv_file('analytics_2017-11-25.csv')
    create_csv_file('analytics_2018-10-15.csv')

    assert csv_compressor().csv_range_years() == range(2017, current_year + 1)


@pytest.mark.django_db
def test_compress_single_file():
    file_name = 'analytics_2018-10-15.csv'
    csv_file = CsvFile(api_name='series', file_name=file_name, file=get_file_mock(file_name))
    create_csv_file('analytics_2018-10-15.csv')

    csv_compressor().compress_single_file(csv_file)

    assert ZipFile.objects.count() == 1
    assert 'analytics_2018.zip' in ZipFile.objects.first().file_name


@pytest.mark.django_db
def test_compress_all():
    create_csv_file('analytics_2017-10-15.csv')
    create_csv_file('analytics_2017-11-25.csv')
    create_csv_file('analytics_2018-10-15.csv')

    csv_compressor().compress_all()

    assert ZipFile.objects.count() == 3
    assert 'analytics_2017.zip' in ZipFile.objects.all()[0].file_name
    assert 'analytics_2018.zip' in ZipFile.objects.all()[1].file_name
    assert 'analytics_2019.zip' in ZipFile.objects.all()[2].file_name
