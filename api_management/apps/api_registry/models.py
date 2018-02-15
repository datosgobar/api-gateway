from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

import api_management.libs.kong.client as kong
import api_management.apps.api_registry.helpers as helpers

class ApiData(models.Model):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z\.\_\~\\\-]+$',
                                  'Only alphanumeric and . - _ ~ characters are allowed.')

    uri_regex = r'([/]{1}[\w\d]+)+\/?'
    uris_validator_regex = helpers.coma_separated_list_of_regex(uri_regex)

    uris_validator = RegexValidator(uris_validator_regex,
                                    'Only alphanumeric and _ characters are allowed. \n'
                                    'Must be prefixed with slash (/)')

    host_regex = r'(?!:\/\/)([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,11}?'
    hosts_validator_regex = helpers.coma_separated_list_of_regex(host_regex)

    hosts_validator = RegexValidator(hosts_validator_regex,
                                     'Only domain names are allowed')

    name = models.CharField(unique=True, max_length=200, validators=[alphanumeric])
    upstream_url = models.URLField()
    hosts = models.CharField(max_length=200, validators=[hosts_validator], blank=True, default='')
    uris = models.CharField(max_length=200, validators=[uris_validator], blank=True, default='')
    strip_uri = models.BooleanField(default=True)
    enabled = models.BooleanField()
    kong_id = models.CharField(max_length=100, null=True)


class ApiManager:

    @staticmethod
    def kong_client():
        return kong.APIAdminClient(settings.KONG_ADMIN_URL)

    @classmethod
    def manage(cls, api_instance, kong_client=None):
        if kong_client is None:
            kong_client = cls.kong_client()
        if api_instance.enabled:
            if api_instance.kong_id:
                cls.__update(api_instance, kong_client)
            else:
                cls.__create(api_instance, kong_client)
        elif api_instance.kong_id:
            cls._delete(api_instance, kong_client)

    @classmethod
    def __update(cls, api_instance, client):
        fields = {"name": api_instance.name,
                  "hosts": api_instance.hosts,
                  "uris": api_instance.uris,
                  "upstream_url": api_instance.upstream_url,
                  "strip_uri": str(api_instance.strip_uri)}
        client.update(api_instance.kong_id, **fields)

    @classmethod
    def __create(cls, api_instance, client):
        response = client.create(api_instance.upstream_url,
                                 name=api_instance.name,
                                 hosts=api_instance.hosts,
                                 uris=api_instance.uris,
                                 strip_uri=api_instance.strip_uri)
        api_instance.kong_id = response['id']

    @classmethod
    def _delete(cls, api_instance, client=None):
        if client is None:
            client = cls.kong_client()
        client.delete(api_instance.kong_id)
        api_instance.kong_id = None

    @staticmethod
    @receiver(pre_save, sender=ApiData)
    def __api_saved(**kwargs):
        ApiManager.manage(kwargs['instance'])

    @staticmethod
    @receiver(pre_delete, sender=ApiData)
    def __api_deleted(**kwargs):
        ApiManager._delete(kwargs['instance'])