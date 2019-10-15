import pytest
from django.urls import reverse

from api_management.apps.api_registry.models import KongConsumer

pytestmark = pytest.mark.django_db


def test_create_consumer_jwt_exists(admin_client, api_data):
    api_data.save()
    body = {
        'api': api_data.id,
        'applicant': 'My consumer name',
        'contact_email': 'my_consumer_email@mail.com',
        'jwtcredential-TOTAL_FORMS': 1,
        'jwtcredential-INITIAL_FORMS': 0,
        'kongconsumerpluginratelimiting-TOTAL_FORMS': 1,
        'kongconsumerpluginratelimiting-INITIAL_FORMS': 0,
        'kongconsumerpluginratelimiting-0-second': 0,
        'kongconsumerpluginratelimiting-0-minute': 0,
        'kongconsumerpluginratelimiting-0-hour': 0,
        'kongconsumerpluginratelimiting-0-day': 0,
        'kongconsumerpluginratelimiting-0-policy': 'local',

    }
    admin_client.post(reverse('admin:api_registry_kongconsumer_add'), body)

    assert KongConsumer.objects.get().jwtcredential
