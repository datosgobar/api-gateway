from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

import api_management.libs.kong.client as kong


class ApiData(models.Model):
    name = models.CharField(unique=True, max_length=200)
    upstream_url = models.URLField()
    uri = models.CharField(max_length=200)
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
                  "uris": api_instance.uri,
                  "upstream_url": api_instance.upstream_url,
                  "strip_uri": str(api_instance.strip_uri)}
        client.update(api_instance.kong_id, **fields)

    @classmethod
    def __create(cls, api_instance, client):
        response = client.create(api_instance.upstream_url,
                                 name=api_instance.name,
                                 uris=api_instance.uri,
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
    def __api_saved(sender, instance, **kwargs):  # pylint: disable=unused-argument
        ApiManager.manage(instance)

    @staticmethod
    @receiver(pre_delete, sender=ApiData)
    def __api_deleted(sender, instance, **kwargs):  # pylint: disable=unused-argument
        ApiManager._delete(instance)
