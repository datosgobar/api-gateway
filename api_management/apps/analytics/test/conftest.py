import pytest
from faker import Faker

from api_management.apps.analytics.test.support import custom_faker
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


@pytest.fixture
def well_formed_query():
    faker = Faker()
    return {
        "ip_address": faker.ipv4(),
        "host": faker.domain_name(),
        "uri": faker.uri_path(),
        "querystring": faker.text(),
        "start_time": faker.iso8601(),
        "request_time": 0.5,
        "status_code": 200,
        "api_data": None,  # Is required!
    }


@pytest.fixture
def api_data(cfaker):
    api = generate_api_data(name=cfaker.api_name(),
                            upstream_url=cfaker.url(),
                            uris=cfaker.api_path(),
                            kong_id=None,
                            api_id=cfaker.random_int())
    api.save()
    return api
