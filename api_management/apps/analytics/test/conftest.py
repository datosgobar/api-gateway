import pytest
from faker import Faker

from api_management.apps.analytics.test.support import custom_faker
from api_management.apps.api_registry.test.support import generate_api_data
from api_management.apps.analytics.models import GoogleAnalyticsManager


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


@pytest.fixture
def well_formed_query(api_data):
    faker = Faker()
    return {
        "ip_address": faker.ipv4(),
        "host": faker.domain_name(),
        "uri": faker.uri_path(),
        "querystring": faker.text(),
        "start_time": faker.iso8601(),
        "request_time": 0.5,
        "status_code": 200,
        "api_data": api_data.pk,  # Is required!
        "user_agent": faker.sentence(),
    }


@pytest.fixture
def api_data(cfaker, db):  # pylint: disable=unused-argument, invalid-name
    api = generate_api_data(name=cfaker.api_name(),
                            upstream_url=cfaker.url(),
                            uris=cfaker.api_path(),
                            kong_id=None,
                            api_id=cfaker.random_int())
    api.save()
    return api


@pytest.fixture
def query(mocker, well_formed_query, api_data):
    query = mocker.stub(name="query-stub")

    query.id = Faker().random_number()
    query.ip_address = well_formed_query['ip_address']
    query.host = well_formed_query['host']
    query.uri = well_formed_query['uri']
    query.querystring = well_formed_query['querystring']
    query.start_time = well_formed_query['start_time']
    query.request_time = well_formed_query['request_time']
    query.status_code = well_formed_query['status_code']
    query.api_data = api_data

    return query


@pytest.fixture
def tracking_id():
    return 'UA-XXXXXXXXX-Y'


@pytest.fixture
def ga_manager(tracking_id):
    return GoogleAnalyticsManager(tracking_id)
