import pytest


@pytest.fixture
def user(db):  # pylint: disable=invalid-name, unused-argument, redefined-outer-name
    """
    Create a test user.
    """
    from django.contrib.auth.models import User
    a_user = User.objects.create_user('test', 'test@github.com', 'test')

    return a_user


@pytest.fixture
def staff_user(user):  # pylint: disable=unused-argument, redefined-outer-name, invalid-name
    """
    Create a test staff user.
    """
    user.is_staff = True
    return user


@pytest.fixture
def well_formed_query():
    return {"ip_address": "127.0.0.1",
            "host": "ramon",
            "uri": "/home/",
            "querystring": "SHOW TABLES",
            "start_time": "2019-11-21T05:04",
            "request_time": "00:30:00"}
