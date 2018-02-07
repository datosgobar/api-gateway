import random

from faker import Factory
from faker.providers import BaseProvider
import pytest

from django.conf import settings

from ..client import APIAdminClient


A_FAKE = Factory.create()
API_URL = settings.KONG_ADMIN_URL


# Custom fake provider
class CustomInfoProvider(BaseProvider):
    def api_name(self):
        return A_FAKE.name().replace(' ', '')

    def api_path(self):
        path = A_FAKE.uri_path()
        if not path.startswith('/'):
            path = '/%s' % path
        return path

    def username(self):
        return A_FAKE.first_name().lower().replace(' ', '')  # + '{ÆÞ}'

    def oauth2_app_name(self):
        return A_FAKE.sentence(nb_words=random.randint(1, 3), variable_nb_words=True).rstrip('.')


A_FAKE.add_provider(CustomInfoProvider)


@pytest.fixture
def fake():
    return A_FAKE


@pytest.fixture
def kong():
    client = APIAdminClient(API_URL)

    for api in client.list()['data']:
        client.delete(api['id'])

    return client
