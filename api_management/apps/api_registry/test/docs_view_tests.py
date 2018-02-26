import requests_mock
import faker

from rest_framework import status
from rest_framework.test import APITestCase

from api_management.apps.api_registry.models import ApiData
from api_management.libs.providers.providers import CustomInfoProvider


class DocsViewTests(APITestCase):

    def setUp(self):
        self.faker = faker.Faker()
        self.faker.add_provider(CustomInfoProvider)

        self.api_data = ApiData(name=self.faker.api_name(),
                                upstream_url=self.faker.url(),
                                uris=self.faker.api_path(),
                                documentation_url=self.faker.url())
        self.api_data.save()

    @requests_mock.mock()
    def test_doc_view(self, mock):
        # Setup
        mock.get(self.api_data.documentation_url, json={'data': 'value'})

        # Exercise
        url = '/api/registry/docs/%s/' % self.api_data.name
        response = self.client.get(url)

        # Verify
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'data': 'value'})
