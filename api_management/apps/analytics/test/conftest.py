from unittest.mock import Mock

import pytest
import requests_mock
from faker import Faker

from api_management.apps.analytics.models import GoogleAnalyticsManager, Query
from api_management.apps.analytics.test.support import custom_faker
from api_management.apps.api_registry.models import KongApi, KongApiHistoricHits
from api_management.apps.api_registry.models import KongApiPluginHttpLog
from api_management.apps.api_registry.test.support import generate_api_data


# pylint: disable=redefined-outer-name

@pytest.fixture()
def cfaker():
    return custom_faker()


@pytest.fixture
def user(db):  # pylint: disable=invalid-name, unused-argument
    """
    Create a test user.
    """
    from django.contrib.auth.models import User
    a_user = User.objects.create_user('test', 'test@github.com', 'test')

    return a_user


@pytest.fixture
def staff_user(user):  # pylint: disable=unused-argument, invalid-name
    """
    Create a test staff user.
    """
    user.is_staff = True
    return user


def query_dict(faker_instance, api_data_pk, query_pk=None, start_time=None):
    query = {

        "ip_address": "192.168.254.254",
        "host": faker_instance.domain_name(),
        "uri": faker_instance.uri_path(),
        "querystring": "%s=%s" % (faker_instance.word(), faker_instance.word()),
        "start_time": start_time or (faker_instance.iso8601() + '-0300'),
        "request_time": "12.0000000000000000000000000",
        "status_code": 200,
        "api_data": api_data_pk,  # Is required!
        "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) "
                      "Gecko/20100101 Firefox/59.0",
        "x_source": "series-tiempo-explorer",
    }
    if query_pk is not None:
        query['id'] = query_pk
    return query


@pytest.fixture
def well_formed_query(api_data, cfaker):
    return query_dict(cfaker, api_data_pk=api_data.pk)


@pytest.fixture
def api_data(cfaker, db):  # pylint: disable=unused-argument, invalid-name
    api = generate_api_data(name=cfaker.api_name(),
                            upstream_url=cfaker.url(),
                            uris=cfaker.api_path(),
                            kong_id=cfaker.uuid4(),
                            api_id=cfaker.random_int())
    with requests_mock.mock() as rmock:
        rmock.delete(requests_mock.ANY, status_code=204)
        api.save()
    return api


@pytest.fixture
def query(well_formed_query, api_data):
    query = Query()

    query.id = Faker().random_number()
    query.ip_address = well_formed_query['ip_address']
    query.host = well_formed_query['host']
    query.uri = well_formed_query['uri']
    query.querystring = well_formed_query['querystring']
    query.start_time = well_formed_query['start_time']
    query.request_time = well_formed_query['request_time']
    query.status_code = well_formed_query['status_code']
    query.api_data = api_data
    query.user_agent = well_formed_query['user_agent']
    query.x_source = "series-tiempo-explorer"

    return query


@pytest.fixture
def tracking_id():
    return 'UA-XXXXXXXXX-Y'


@pytest.fixture
def ga_manager(tracking_id):
    return GoogleAnalyticsManager(tracking_id)


# pylint: disable=unused-argument, invalid-name
@pytest.fixture
def httplogdata(mocker, api_data, cfaker, db):
    httplogdata = KongApiPluginHttpLog()
    httplogdata.enabled = True
    httplogdata.exclude_regex = ''
    httplogdata.api_key = ''
    httplogdata.parent = api_data

    with requests_mock.mock() as rmock:
        rmock.post(requests_mock.ANY,
                   status_code=201,
                   json={'id': cfaker.uuid4()})
        httplogdata.save()

    return httplogdata


@pytest.fixture
def kong_api():
    instance = Mock(KongApi)
    instance.id = 1
    instance.name = 'series'
    instance._state = Mock()
    return instance


@pytest.fixture
def historic_hits():
    instance = Mock(KongApiHistoricHits)
    instance.id = 1
    instance._state = Mock()
    instance.kong_api = kong_api()
    instance.accumulated_hits = 100
    return instance


@pytest.fixture
def empty_historic_hits():
    instance = Mock(KongApiHistoricHits)
    instance.id = 2
    instance._state = Mock()
    instance.kong_api = kong_api()
    instance.accumulated_hits = 0
    return instance
