import urllib.parse

from abc import abstractmethod

import kong.kong_clients as kong
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.urls import reverse

from api_management.apps.api_registry.validators import HostsValidator, \
    UrisValidator, \
    AlphanumericValidator

API_GATEWAY_LOG_PLUGIN_NAME = 'api-gateway-httplog'


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

    def __str__(self):
        return self.name

    def clean(self):
        if not (self.uris or self.hosts):
            raise ValidationError("At least one of 'hosts' or 'uris' must be specified")

        return super(ApiData, self).clean()

    def get_enabled_plugins(self):
        plugins = []

        try:
            plugins.append(self.ratelimitingdata)
        except RateLimitingData.DoesNotExist:
            pass
        try:
            plugins.append(self.jwtdata)
        except JwtData.DoesNotExist:
            pass

        try:
            plugins.append(self.httplogdata)
        except HttpLogData.DoesNotExist:
            pass

        return plugins


class ApiManager:

    @classmethod
    def using_settings(cls):
        return cls(settings.KONG_TRAFFIC_URL,
                   kong.KongAdminClient(settings.KONG_ADMIN_URL),
                   settings.HTTPLOG2_ENDPOINT)

    def __init__(self, kong_traffic_url, kong_client, httplog2_endpoint):
        if isinstance(kong_traffic_url, str) \
                and not kong_traffic_url.endswith('/'):
            kong_traffic_url += '/'

        self.kong_traffic_url = kong_traffic_url
        self.kong_client = kong_client
        self.httplog2_endpoint = httplog2_endpoint

    @staticmethod
    def doc_suffix():
        return '-doc'

    def manage_plugins(self, api_instance):
        enabled_plugins = api_instance.get_enabled_plugins()

        for plugin in enabled_plugins:
            self._manage_plugin(plugin)

    # pylint: disable=too-many-arguments
    def _manage_plugin(self, plugin):

        if plugin.kong_id is not None:
            self.kong_client.plugins.delete(plugin.kong_id,
                                            api_pk=plugin.api.kong_id)
        if plugin.api.enabled:
            response = self.kong_client \
                .plugins.create(plugin.name,
                                api_name_or_id=plugin.api.kong_id,
                                config=plugin.config())

            plugin.kong_id = response['id']

    def manage_apis(self, api_instance):
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
        response = self.kong_client \
            .apis.create(api_instance.name,
                         upstream_url=api_instance.upstream_url,
                         hosts=api_instance.hosts,
                         uris=self.api_uri_pattern(api_instance),
                         strip_uri=api_instance.strip_uri,
                         preserve_host=api_instance.preserve_host)
        api_instance.kong_id = response['id']

    def update_main_api(self, api_instance):
        self.kong_client \
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
        self.kong_client \
            .apis.create(api_instance.name + self.doc_suffix(),
                         upstream_url=self.doc_upstream(api_instance),
                         uris=self.docs_uri_pattern(api_instance),
                         hosts=api_instance.hosts)

    def update_docs_api(self, api_instance):
        self.kong_client \
            .apis.update(api_instance.name + self.doc_suffix(),
                         upstream_url=self.doc_upstream(api_instance),
                         uris=self.docs_uri_pattern(api_instance),
                         hosts=api_instance.hosts)

    def delete_docs_api(self, api_instance):
        self.kong_client.apis.delete(api_instance.name + self.doc_suffix())


@receiver(post_save, sender=ApiData)
def api_saved_add_plugins(sender, instance, **_):
    ApiManager.using_settings().manage_apis(instance)
    ApiManager.using_settings().manage_plugins(instance)

    post_save.disconnect(api_saved_add_plugins, sender=sender)
    instance.save()
    post_save.connect(api_saved_add_plugins, sender=sender)


@receiver(pre_delete, sender=ApiData)
def api_deleted(**kwargs):
    ApiManager.using_settings().delete(kwargs['instance'])


class TokenRequest(models.Model):

    api = models.ForeignKey(ApiData, on_delete=models.CASCADE)
    applicant = models.CharField(max_length=100, blank=False)
    contact_email = models.EmailField(blank=False)
    consumer_application = models.CharField(max_length=200, blank=False)
    requests_per_day = models.IntegerField()


class PluginData(models.Model):

    apidata = models.OneToOneField(ApiData, on_delete=models.CASCADE)
    kong_id = models.UUIDField(null=True)

    class Meta:
        abstract = True

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def config(self):
        pass


class RateLimitingData(PluginData):

    second = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minute = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    hour = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    day = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def clean(self):
        config = {'second': self.second,
                  'minute': self.minute,
                  'hour': self.hour,
                  'day': self.day}

        cleaned_config = {}
        for key, value in config.items():
            if value:
                cleaned_config[key] = value

        prev_k = None
        prev_v = 0
        for key, value in cleaned_config.items():
            if value < prev_v:
                raise ValidationError('The limit for %s cannot be lower '
                                      'than the limit for %s' % (key, prev_k))
            prev_k = key
            prev_v = value

    @property
    def name(self):
        return 'rate-limiting'

    def config(self):
        return {'second': self.second,
                'minute': self.minute,
                'hour': self.hour,
                'day': self.day}

class HttpLogData(PluginData):

    api_key = models.CharField(max_length=100, blank=False, null=False)
    exclude_regex = models.CharField(max_length=100, null=False, blank=True)

    @property
    def name(self):
        return API_GATEWAY_LOG_PLUGIN_NAME

    def config(self):
        return {'token': self.api_key,
                'endpoint': settings.HTTPLOG2_ENDPOINT,
                'api_data': self.api.pk}


class JwtData(PluginData):

    @property
    def name(self):
        return 'jwt'

    def config(self):
        return {}
