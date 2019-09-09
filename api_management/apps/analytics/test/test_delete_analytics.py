import pytest
from django.core.management import call_command, CommandError

from api_management.apps.analytics.models import Query
from api_management.apps.analytics.test.conftest import query_dict
from api_management.apps.analytics.test.support import custom_faker
from api_management.apps.api_registry.models import KongApi


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def setup_data():
    kong_api = KongApi.objects.create(name='test_api',
                                      uri='/test_uri',
                                      upstream_url='http://test.upstream.url/')
    Query.objects.create(**query_dict(custom_faker(), kong_api))
    Query.objects.create(**query_dict(custom_faker(), kong_api))
    Query.objects.create(**query_dict(custom_faker(), kong_api,
                                      start_time='2019-01-01 00:50:00'))


def test_delete_analytics():
    call_command('delete_analytics', 'test_api', '2019-01-01', confirm=True)

    assert Query.objects.count() == 2


def test_delete_analytics_with_date_with_no_queries():
    call_command('delete_analytics', 'test_api', '2019-01-02', confirm=True)
    assert Query.objects.count() == 3


def test_delete_analytics_with_bad_api_name():
    call_command('delete_analytics', 'bad_api_name', '2019-01-01', confirm=True)
    assert Query.objects.count() == 3


def test_delete_analytics_invalid_date_input():
    with pytest.raises(CommandError):
        call_command('delete_analytics', 'test_api', 'not_a_date', confirm=True)


def test_delete_analytics_datetime_input():
    with pytest.raises(CommandError):
        call_command('delete_analytics', 'test_api', '2019-01-01 00:40:00', confirm=True)
