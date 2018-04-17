from enum import Enum

import urllib.parse

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
from api_management.apps.api_registry.signals import token_request_accepted

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
    rate_limiting_enabled = models.BooleanField(default=False)
    rate_limiting_second = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rate_limiting_minute = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rate_limiting_hour = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rate_limiting_day = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    rate_limiting_kong_id = models.CharField(max_length=100, null=True)
    httplog2_enabled = models.BooleanField(default=False)
    httplog2_api_key = models.CharField(max_length=100, blank=True)
    httplog2_kong_id = models.CharField(max_length=100, null=True)
    httplog2_ga_exclude_regex = models.CharField(max_length=100, null=False, blank=True)
    jwt_enabled = models.BooleanField(default=False)
    jwt_kong_id = models.CharField(max_length=100, null=True)

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

        if self.httplog2_enabled and not self.httplog2_api_key:
            raise ValidationError('must provide api key to enable logs')

        return super(ApiData, self).clean()


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
        plugins = self._plugins_data(api_instance)

        api_instance.rate_limiting_kong_id = self._manage_plugin(**plugins['rate-limiting'])
        api_instance.httplog2_kong_id = self._manage_plugin(**plugins[API_GATEWAY_LOG_PLUGIN_NAME])
        api_instance.jwt_kong_id = self._manage_plugin(**plugins['jwt'])
        api_instance.httplog2_kong_id = self._manage_plugin(**plugins[API_GATEWAY_LOG_PLUGIN_NAME])

    def _plugins_data(self, api_instance):
        rate_limiting = self.rate_limiting_data(api_instance)
        httplog2 = self.httplog2_data(api_instance)
        jwt = self.jwt_data(api_instance)
        return {'rate-limiting': rate_limiting,
                API_GATEWAY_LOG_PLUGIN_NAME: httplog2,
                'jwt': jwt}

    def jwt_data(self, api_instance):
        return {
            'api_enabled': api_instance.enabled,
            'api_kong_id': api_instance.kong_id,
            'plugin_name': 'jwt',
            'plugin_kong_id': api_instance.jwt_kong_id,
            'plugin_enabled': api_instance.jwt_enabled,
            'plugin_config': {
            },
        }

    def httplog2_data(self, api_instance):
        return {
            'api_enabled': api_instance.enabled,
            'api_kong_id': api_instance.kong_id,
            'plugin_name': API_GATEWAY_LOG_PLUGIN_NAME,
            'plugin_kong_id': api_instance.httplog2_kong_id,
            'plugin_enabled': api_instance.httplog2_enabled,
            'plugin_config': {
                'token': api_instance.httplog2_api_key,
                'endpoint': self.httplog2_endpoint,
                'api_data': api_instance.pk,
            },
        }

    def rate_limiting_data(self, api_instance):
        return {'api_enabled': api_instance.enabled,
                'api_kong_id': api_instance.kong_id,
                'plugin_name': 'rate-limiting',
                'plugin_kong_id': api_instance.rate_limiting_kong_id,
                'plugin_enabled': api_instance.rate_limiting_enabled,
                'plugin_config': {
                    'second': api_instance.rate_limiting_second or None,
                    'minute': api_instance.rate_limiting_minute or None,
                    'hour': api_instance.rate_limiting_hour or None,
                    'day': api_instance.rate_limiting_day or None}}

    # pylint: disable=too-many-arguments
    def _manage_plugin(self, api_enabled, api_kong_id,
                       plugin_config, plugin_enabled,
                       plugin_kong_id, plugin_name):
        response_id = None
        if plugin_kong_id is not None:
            self.kong_client.plugins.delete(plugin_kong_id,
                                            api_pk=api_kong_id)
        if plugin_enabled and api_enabled:
            response = self.kong_client \
                .plugins.create(plugin_name,
                                api_name_or_id=api_kong_id,
                                config=plugin_config)

            response_id = response['id']
        return response_id

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


class TokenRequestState(Enum):
    PENDING = ('Pendiente', )
    ACCEPTED = ('Aceptada', )
    REJECTED = ('Rechazada', )

    def __init__(self, kind_name):
        self.kind_name = kind_name


class TokenRequest(models.Model):

    api = models.ForeignKey(ApiData, on_delete=models.CASCADE)
    applicant = models.CharField(max_length=100, blank=False)
    contact_email = models.EmailField(blank=False)
    consumer_application = models.CharField(max_length=200, blank=False)
    requests_per_day = models.IntegerField()
    state = models.CharField(default=TokenRequestState.PENDING.name,
                             choices=((x.name, x.kind_name) for x in TokenRequestState),
                             max_length=20)

    def is_pending(self):
        return TokenRequestState[self.state] == TokenRequestState.PENDING

    def accept(self):
        if not self.is_pending():
            raise ValidationError('only pending requests can be accepted')

        self.state = TokenRequestState.ACCEPTED.name
        self.save()

        token_request_accepted.send(sender=self)

    def reject(self):
        if not self.is_pending():
            raise ValidationError('only pending requests can be rejected')

        self.state = TokenRequestState.REJECTED.name
        self.save()
