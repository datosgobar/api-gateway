import urllib.parse

from django.urls import reverse
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator

import kong.kong_clients as kong
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
    rate_limiting_enabled = models.BooleanField(default=False)
    rate_limiting_second = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rate_limiting_minute = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rate_limiting_hour = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rate_limiting_day = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rate_limiting_kong_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

    def clean(self):
        if not (self.uris or self.hosts):
            raise ValidationError("At least one of 'hosts' or 'uris' must be specified")

        if self.rate_limiting_enabled:
            config = {'second': self.rate_limiting_second,
                      'minute': self.rate_limiting_minute,
                      'hour': self.rate_limiting_hour,
                      'day': self.rate_limiting_day}

            cleaned_config = {}
            for key, value in config.items():
                if value:
                    cleaned_config[key] = value

            if not cleaned_config:
                raise ValidationError(
                    "At least one of 'second', 'minute', "
                    "'hour' or 'day' must be provided to enable rate limiting")

            prev_k = None
            prev_v = 0
            for key, value in cleaned_config.items():
                if value < prev_v:
                    raise ValidationError('The limit for %s cannot be lower '
                                          'than the limit for %s' % (key, prev_k))
                prev_k = key
                prev_v = value

        return super(ApiData, self).clean()


class ApiManager:

    @classmethod
    def using_settings(cls):
        return cls(settings.KONG_TRAFFIC_URL,
                   kong.KongAdminClient(settings.KONG_ADMIN_URL))

    def __init__(self, kong_traffic_url, kong_client):
        if isinstance(kong_traffic_url, str) \
                and not kong_traffic_url.endswith('/'):
            kong_traffic_url += '/'

        self.kong_traffic_url = kong_traffic_url
        self.kong_client = kong_client

    @staticmethod
    def doc_suffix():
        return '-doc'

    def manage(self, api_instance):
        self._manage_apis(api_instance)
        self._manage_plugins(api_instance)

    def _manage_plugins(self, api_instance):

        if api_instance.rate_limiting_kong_id is not None:
            self._delete_rate_limiting_plugin(api_instance)

        if api_instance.rate_limiting_enabled \
                and api_instance.enabled:
            self._create_rate_limiting_plugin(api_instance)

    def _delete_rate_limiting_plugin(self, api_instance):
        self.kong_client\
            .plugins.delete(api_instance.rate_limiting_kong_id,
                            api_pk=api_instance.kong_id)
        api_instance.rate_limiting_kong_id = None

    def _create_rate_limiting_plugin(self, api_instance):
        config = {'second': api_instance.rate_limiting_second,
                  'minute': api_instance.rate_limiting_minute,
                  'hour': api_instance.rate_limiting_hour,
                  'day': api_instance.rate_limiting_day}

        for key, value in config.items():
            config[key] = value or None  # no enviar 0

        response = self.kong_client\
            .plugins.create('rate-limiting',
                            api_name_or_id=api_instance.kong_id,
                            config=config)

        api_instance.rate_limiting_kong_id = response['id']

    def _manage_apis(self, api_instance):
        if api_instance.enabled:
            if api_instance.kong_id:
                self.__update(api_instance)
            else:
                self.__create(api_instance)
        elif api_instance.kong_id:
            self.delete(api_instance)

    def doc_upstream(self, api_instance):
        doc_endpoint = reverse('api-doc', args=[api_instance.name])
        return urllib.parse.urljoin(self.kong_traffic_url, doc_endpoint)

    @staticmethod
    def api_uri_pattern(api_instance):
        return api_instance.uris + '/(?=.)'

    @staticmethod
    def docs_uri_pattern(api_instance):
        return api_instance.uris + '/$'

    def __update(self, api_instance):
        self.update_docs_api(api_instance)
        self.update_main_api(api_instance)

    def __create(self, api_instance):
        self.create_docs_api(api_instance)
        self.create_main_api(api_instance)

    def delete(self, api_instance):
        if api_instance.kong_id:
            self.delete_docs_api(api_instance)
            self.delete_main_api(api_instance)

    def create_main_api(self, api_instance):
        response = self.kong_client\
            .apis.create(api_instance.name,
                         upstream_url=api_instance.upstream_url,
                         hosts=api_instance.hosts,
                         uris=self.api_uri_pattern(api_instance),
                         strip_uri=api_instance.strip_uri,
                         preserve_host=api_instance.preserve_host)
        api_instance.kong_id = response['id']

    def update_main_api(self, api_instance):
        self.kong_client\
            .apis.update(api_instance.kong_id,
                         upstream_url=api_instance.upstream_url,
                         hosts=api_instance.hosts,
                         uris=self.api_uri_pattern(api_instance),
                         strip_uri=api_instance.strip_uri,
                         preserve_host=api_instance.preserve_host)

    def delete_main_api(self, api_instance):

        self.kong_client.apis.delete(api_instance.kong_id)

        api_instance.kong_id = None

    def create_docs_api(self, api_instance):
        self.kong_client\
            .apis.create(api_instance.name + self.doc_suffix(),
                         upstream_url=self.doc_upstream(api_instance),
                         uris=self.docs_uri_pattern(api_instance),
                         hosts=api_instance.hosts)

    def update_docs_api(self, api_instance):
        self.kong_client\
            .apis.update(api_instance.name + self.doc_suffix(),
                         upstream_url=self.doc_upstream(api_instance),
                         uris=self.docs_uri_pattern(api_instance),
                         hosts=api_instance.hosts)

    def delete_docs_api(self, api_instance):
        self.kong_client.apis.delete(api_instance.name + self.doc_suffix())


@receiver(pre_save, sender=ApiData)
def api_saved(**kwargs):
    ApiManager.using_settings().manage(kwargs['instance'])


@receiver(pre_delete, sender=ApiData)
def api_deleted(**kwargs):
    ApiManager.using_settings().delete(kwargs['instance'])
