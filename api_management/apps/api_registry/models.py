from django.db import models

import api_management.libs.kong.client as kong

KONG_ADMIN_URL = 'http://localhost:8001/'


class ApiManager:

    @staticmethod
    def _kong_client():
        return kong.APIAdminClient(KONG_ADMIN_URL)

    @classmethod
    def manage(cls, api_instance):
        if api_instance.enabled:
            if api_instance.kong_id:
                cls.update(api_instance)
            else:
                cls.create(api_instance)
        elif api_instance.kong_id:
            cls.delete(api_instance)

    @classmethod
    def update(cls, api_instance):
        client = ApiManager._kong_client()
        fields = {"name": api_instance.name,
                  "uris": api_instance.uri,
                  "upstream_url": api_instance.upstream_url,
                  "strip_uri": str(api_instance.strip_uri)}
        client.update(api_instance.kong_id, **fields)

    @classmethod
    def create(cls, api_instance):
        client = ApiManager._kong_client()
        response = client.create(api_instance.upstream_url,
                                 name=api_instance.name,
                                 uris=api_instance.uri,
                                 strip_uri=api_instance.strip_uri)
        api_instance.kong_id = response['id']

    @classmethod
    def delete(cls, api_instance):
        client = ApiManager._kong_client()
        client.delete(api_instance.kong_id)
        api_instance.kong_id = None


class Api(models.Model):
    name = models.CharField(unique=True, max_length=200)
    upstream_url = models.URLField()
    uri = models.CharField(max_length=200)
    strip_uri = models.BooleanField(default=True)
    enabled = models.BooleanField()
    kong_id = models.CharField(max_length=100, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        ApiManager.manage(self)
        return super(Api, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        ApiManager.delete(self)
        return super(Api, self).delete(using, keep_parents)
