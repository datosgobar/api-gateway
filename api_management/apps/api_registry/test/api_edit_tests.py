from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from api_management.apps.api_registry.models import KongApi


class DocsViewTests(APITestCase):

    def setUp(self):
        api_data_dict = {'name': 'api_name',
                         'upstream_url': 'http://api.com',
                         'uri': '/api_uri',
                         'documentation_url': 'http://docs.url.com'}
        KongApi(**api_data_dict).save()

        self.url = reverse('api-edit', kwargs={'name': 'api_name'})
        self.request_data = {'name': 'update_name',
                             'upstream_url': 'http://full.url.com',
                             'uri': '/update_uri',
                             'documentation_url': 'http://new.docs.com'}

        admin_user = User.objects.create(
            username='staff',
            password='staff',
            email='staff@test.com',
            is_staff=True)

        regular_user = User.objects.create(
            username='regular',
            password='regular',
            email='regular@test.com',
            is_staff=False)
        self.admin_token = Token.objects.create(user=admin_user)
        self.regular_token = Token.objects.create(user=regular_user)
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

    def test_put_method_complete_update(self):
        response = self.client.put(self.url, self.request_data, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, KongApi.objects.count())
        self.assertEqual('update_name', KongApi.objects.get().name)
        self.assertEqual('http://full.url.com',
                         KongApi.objects.get().upstream_url)
        self.assertEqual('/update_uri', KongApi.objects.get().uri)
        self.assertEqual('http://new.docs.com',
                         KongApi.objects.get().documentation_url)

    def test_patch_method_partial_update(self):
        partial_data = {'upstream_url': 'http://patch.url.com'}
        response = self.client.patch(self.url, partial_data, format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, KongApi.objects.count())
        self.assertEqual('http://patch.url.com',
                         KongApi.objects.get().upstream_url)

        partial_data = {'uri': '/patch_uri'}
        self.client.patch(self.url, partial_data, format='json')
        self.assertEqual('/patch_uri', KongApi.objects.get().uri)

    def test_unimplemented_http_methods(self):
        unimplemented_methods = (
            self.client.get,
            self.client.delete,
            self.client.post,
        )
        for method in unimplemented_methods:
            response = method(self.url, self.request_data, format='json')
            self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED,
                             response.status_code)

    def test_forbidden_access_anonymous_users(self):
        self.client.credentials()
        partial_data = {'upstream_url': 'http://patch.url.com'}
        response = self.client.patch(self.url, partial_data, format='json')
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_forbidden_access_non_admin_users(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.regular_token.key)
        partial_data = {'upstream_url': 'http://patch.url.com'}
        response = self.client.patch(self.url, partial_data, format='json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
