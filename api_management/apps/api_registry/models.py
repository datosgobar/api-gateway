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
    enabled = models.BooleanField()
    kong_id = models.CharField(max_length=100, null=True)
    documentation_url = models.URLField(blank=True)

    def clean(self):
        if not (self.uris or self.hosts):
            raise ValidationError("At least one of 'hosts' or 'uris' must be specified")


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
