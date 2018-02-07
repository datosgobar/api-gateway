from django.db import models
from django.conf import settings

import api_management.libs.kong.client as kong


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
            cls.__delete(api_instance, kong_client)

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
    def __delete(cls, api_instance, client):
        client.delete(api_instance.kong_id)
        api_instance.kong_id = None


class ApiData(ApiManager, models.Model):
    name = models.CharField(unique=True, max_length=200)
    upstream_url = models.URLField()
    uri = models.CharField(max_length=200)
    strip_uri = models.BooleanField(default=True)
    enabled = models.BooleanField()
    kong_id = models.CharField(max_length=100, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.manage(self)
        return super(ApiData, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.enabled = False
        self.manage(self)
        return super(ApiData, self).delete(using, keep_parents)
