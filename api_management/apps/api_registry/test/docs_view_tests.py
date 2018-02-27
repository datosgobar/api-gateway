import requests
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

        self.api_doc_url = '/api/registry/docs/%s/' % self.api_data.name

    def tearDown(self):
        self.api_data.delete()

    @requests_mock.mock()
    def test_doc_view(self, mock):
        # Setup
        mock.get(self.api_data.documentation_url, json={'data': 'value'})

        # Exercise
        response = self.client.get(self.api_doc_url)

        # Verify
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # pylint: disable=invalid-name
    def test_doc_view_wo_documentation_url_returns_404(self):
        # Setup
        self.api_data.documentation_url = ""
        self.api_data.save()

        # Exercise
        response = self.client.get(self.api_doc_url)

        # Verify
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @requests_mock.mock()
    def test_doc_view_w_doc_server_down(self, mock):
        # Setup
        mock.get(self.api_data.documentation_url, exc=requests.exceptions.ConnectionError)

        # Exercise
        response = self.client.get(self.api_doc_url)

        # Verify
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    @requests_mock.mock()
    # pylint: disable=invalid-name
    def test_doc_view_w_doc_server_returning_invalid_values(self, mock):
        # Setup
        mock.get(self.api_data.documentation_url, status_code=status.HTTP_204_NO_CONTENT)

        # Exercise
        response = self.client.get(self.api_doc_url)

        # Verify
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
