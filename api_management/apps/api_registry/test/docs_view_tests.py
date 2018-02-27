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

    def test_doc_view(self):

        # Exercise
        response = self.client.get(self.api_doc_url)

        # Verify
        self.assertEqual(response.status_code, status.HTTP_200_OK)
