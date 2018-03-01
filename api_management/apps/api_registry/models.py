from django.urls import reverse
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

import api_management.libs.kong.client as kong
from api_management.apps.api_registry.validators import HostsValidator,\
                                                        UrisValidator,\
                                                        AlphanumericValidator


class ApiData(models.Model):

    name = models.CharField(unique=True, max_length=200, validators=[AlphanumericValidator()])
    upstream_url = models.URLField()
    hosts = models.CharField(max_length=200, validators=[HostsValidator()], blank=True, default='')
    uris = models.CharField(max_length=200, validators=[UrisValidator()], blank=True, default='')
    strip_uri = models.BooleanField(default=True)
    preserve_host = models.BooleanField(default=False)
    enabled = models.BooleanField(default=False)
    kong_id = models.CharField(max_length=100, null=True)
    documentation_url = models.URLField(blank=True)

    def clean(self):
        if not (self.uris or self.hosts):
            raise ValidationError("At least one of 'hosts' or 'uris' must be specified")

        return super(ApiData, self).clean()


class ApiManager:

    @classmethod
    def using_settings(cls):
        return cls(settings.KONG_TRAFFIC_URL,
                   kong.APIAdminClient(settings.KONG_ADMIN_URL))

    def __init__(self, kong_traffic_url, kong_client):
        self.kong_traffic_url = kong_traffic_url
        self.kong_client = kong_client

    def __setattr__(self, key, value):
        if key in ('kong_traffic_url',)\
                and isinstance(value, str)\
                and not value.endswith('/'):
            value += '/'
        return super(ApiManager, self).__setattr__(key, value)

    @staticmethod
    def doc_suffix():
        return '-doc'

    def manage(self, api_instance, kong_client=None):

        kong_client = kong_client or self.kong_client

        self._manage_doc_api(api_instance, kong_client)
        self._manage_main_api(api_instance, kong_client)

    def _manage_main_api(self, api_instance, kong_client):
        if api_instance.enabled:
            if api_instance.kong_id:
                self.__update(api_instance, kong_client)
            else:
                self.__create(api_instance, kong_client)
        elif api_instance.kong_id:
            self.delete_main_api(api_instance, kong_client)

    def _manage_doc_api(self, api_instance, kong_client):
        if not api_instance.id:  # if just created
            kong_client.create(self.doc_upstream(api_instance),
                               uris=self.docs_uri_pattern(api_instance),
                               name=api_instance.name + self.doc_suffix())

    def doc_upstream(self, api_instance):
        doc_endpoint = reverse('api-doc', args=[api_instance.name])[1:]
        return self.kong_traffic_url + doc_endpoint

    @staticmethod
    def docs_uri_pattern(api_instance):
        return api_instance.uris + '/?$'

    @classmethod
    def __update(cls, api_instance, client):
        fields = {"name": api_instance.name,
                  "hosts": api_instance.hosts,
                  "uris": api_instance.uris,
                  "upstream_url": api_instance.upstream_url,
                  "strip_uri": str(api_instance.strip_uri),
                  "preserve_host": str(api_instance.preserve_host)}
        client.update(api_instance.kong_id, **fields)

    @classmethod
    def __create(cls, api_instance, client):
        response = client.create(api_instance.upstream_url,
                                 name=api_instance.name,
                                 hosts=api_instance.hosts,
                                 uris=api_instance.uris,
                                 strip_uri=api_instance.strip_uri,
                                 preserve_host=api_instance.preserve_host)
        api_instance.kong_id = response['id']

    def delete_main_api(self, api_instance, kong_client=None):
        kong_client = kong_client or self.kong_client

        kong_client.delete(api_instance.kong_id)
        api_instance.kong_id = None

    def delete_docs_api(self, api_instance, kong_client=None):
        kong_client = kong_client or self.kong_client

        kong_client.delete(api_instance.name + self.doc_suffix())


@receiver(pre_save, sender=ApiData)
def api_saved(**kwargs):
    ApiManager.using_settings().manage(kwargs['instance'])


@receiver(pre_delete, sender=ApiData)
def api_deleted(**kwargs):
    manager = ApiManager.using_settings()
    manager.delete_docs_api(kwargs['instance'])
    manager.delete_main_api(kwargs['instance'])
