import faker
import requests_mock
from django.shortcuts import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api_management.apps.api_registry.models import ApiData
from api_management.libs.providers.providers import CustomInfoProvider


class DocsViewTests(APITestCase):

    @requests_mock.mock()
    def setUp(self, request_mock):  # pylint: disable=arguments-differ

        self.faker = faker.Faker()
        self.faker.add_provider(CustomInfoProvider)

        self.api_data_dict = {'name': self.faker.api_name(),
                              'upstream_url': self.faker.url(),
                              'uri': self.faker.api_path(),
                              'documentation_url': self.faker.url()}

        self.api_data = ApiData(**self.api_data_dict)

        request_mock.post(requests_mock.ANY,
                          status_code=status.HTTP_201_CREATED,
                          json={**self.api_data_dict, **{'id': self.faker.uuid4()}})

        request_mock.get(requests_mock.ANY,
                         status_code=status.HTTP_200_OK,
                         json={'total': 0, 'data': []})

        self.api_data.save()

        self.api_doc_url = reverse('api-doc', args=[self.api_data.name])
        # self.api_doc_url = self.api_doc_url.replace(settings.FORCE_SCRIPT_NAME, '')

    @requests_mock.mock()
    def tearDown(self, request_mock):  # pylint: disable=arguments-differ
        request_mock.delete(requests_mock.ANY, status_code=status.HTTP_204_NO_CONTENT)

        self.api_data.delete()

    def test_doc_view(self):
        # Exercise
        response = self.client.get(self.api_doc_url)

        # Verify
        self.assertEqual(response.status_code, status.HTTP_200_OK)
