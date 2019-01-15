import urllib.parse
from abc import abstractmethod
from collections import OrderedDict

from django.conf import settings
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from solo.models import SingletonModel

from api_management.apps.api_registry.helpers import kong_client_using_settings
from api_management.apps.api_registry.mixins import KongConsumerChildMixin
from api_management.apps.api_registry.validators import HostsValidator, \
    UrisValidator, \
    AlphanumericValidator

API_GATEWAY_LOG_PLUGIN_NAME = 'api-gateway-httplog'


class KongObject(models.Model):
    enabled = models.BooleanField(default=False)
    kong_id = models.UUIDField(null=True)

    class Meta:
        abstract = True

    def is_enabled(self):
        return self.enabled

    def get_kong_id(self):
        return str(self.kong_id)

    def manage_kong(self, kong_client):
        if self.is_enabled():
            self.update_or_create_kong(kong_client)

        elif self.kong_id:
            self.delete_kong(kong_client)

    def update_or_create_kong(self, kong_client):
        if self.kong_id:
            response = self.update_kong(kong_client)
        else:
            response = self.create_kong(kong_client)
        self.kong_id = self.get_kong_id_from_response(response)

    @staticmethod
    def get_kong_id_from_response(response):
        return response.id

    @abstractmethod
    def create_kong(self, kong_client):
        pass

    @abstractmethod
    def update_kong(self, kong_client):
        pass

    @abstractmethod
    def delete_kong(self, kong_client):
        pass


class KongApi(KongObject):
    name = models.CharField(unique=True, max_length=200, validators=[AlphanumericValidator()])
    upstream_url = models.URLField()
    hosts = models.CharField(max_length=200, validators=[HostsValidator()], blank=True, default='')
    uri = models.CharField(max_length=200, validators=[UrisValidator()], blank=True, default='')
    strip_uri = models.BooleanField(default=True)
    preserve_host = models.BooleanField(default=False)
    documentation_url = models.URLField(blank=True)
    docs_kong_id = models.UUIDField(null=True)  # TODO: Refactor, split responsability
    use_swagger = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def clean(self):
        if not (self.uri or self.hosts):
            raise ValidationError("At least one of 'hosts' or 'uris' must be specified")

        return super(KongApi, self).clean()

    def create_kong(self, kong_client):
        self._create_docs_api(kong_client)
        return self._create_main_api(kong_client)

    def _create_main_api(self, kong_client):
        response = kong_client \
            .apis.create(name=self.name,
                         upstream_url=self.upstream_url,
                         hosts=self.hosts,
                         uris=self._api_uri_pattern(),
                         strip_uri=self.strip_uri,
                         preserve_host=self.preserve_host)
        self.kong_id = response.id
        return response

    def _api_uri_pattern(self):
        return self.uri + '/(?=.)'

    def _create_docs_api(self, kong_client):
        response = kong_client \
            .apis.create(name=(self.name + self._docs_suffix()),
                         upstream_url=self._docs_upstream(),
                         uris=self._docs_uri_pattern(),
                         hosts=self.hosts)
        self.docs_kong_id = response.id

    def get_docs_kong_id(self):
        return str(self.docs_kong_id)

    @staticmethod
    def _docs_suffix():
        return '-doc'

    def _docs_upstream(self):
        doc_endpoint = reverse('api-doc', args=[self.name])
        return urllib.parse.urljoin(settings.KONG_TRAFFIC_URL, doc_endpoint)

    def _docs_uri_pattern(self):
        return self.uri + '/?$'

    def update_kong(self, kong_client):
        self._update_docs_api(kong_client)
        return self._update_main_api(kong_client)

    def _update_main_api(self, kong_client):
        return kong_client \
            .apis.update(self.get_kong_id(),
                         upstream_url=self.upstream_url,
                         hosts=self.hosts,
                         uris=self._api_uri_pattern(),
                         strip_uri=self.strip_uri,
                         preserve_host=self.preserve_host)

    def _update_docs_api(self, kong_client):
        return kong_client \
            .apis.update(self.get_docs_kong_id(),
                         upstream_url=self._docs_upstream(),
                         uris=self._docs_uri_pattern(),
                         hosts=self.hosts)

    def delete_kong(self, kong_client):

        self._delete_docs_api(kong_client)
        self._delete_main_api(kong_client)

    def _delete_main_api(self, kong_client):
        kong_client.apis.delete(self.get_kong_id())
        self.kong_id = None

    def _delete_docs_api(self, kong_client):
        kong_client.apis.delete(self.get_docs_kong_id())
        self.docs_kong_id = None

    @property
    def plugins(self):
        # TODO: No deberian existir siempre?
        plugins = []
        try:
            plugins.append(self.kongapiplugincors)
        except KongApiPluginCors.DoesNotExist:
            pass
        try:
            plugins.append(self.kongapipluginhttplog)
        except KongApiPluginHttpLog.DoesNotExist:
            pass
        try:
            plugins.append(self.kongapipluginratelimiting)
        except KongApiPluginRateLimiting.DoesNotExist:
            pass
        try:
            plugins.append(self.kongapipluginjwt)
        except KongApiPluginJwt.DoesNotExist:
            pass

        return plugins


# pylint: disable=invalid-name
@receiver(post_save, sender=KongApi)
def re_create_kong_plugins_when_re_enabling_existing_api(created, instance, *_, **__):
    if not created:
        for plugin in instance.plugins:
            plugin.save()


class KongApiPlugin(models.Model):
    parent = models.OneToOneField(KongApi, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def create_kong(self, kong_client):
        return kong_client.plugins.create(name=self.get_plugin_name(),
                                          api_name_or_id=self.parent.get_kong_id(),
                                          config=self.config())

    def update_kong(self, kong_client):
        return kong_client.plugins.update(self.get_kong_id(),
                                          api_pk=self.parent.get_kong_id(),
                                          config=self.config())


class KongPlugin(KongObject):
    plugin_name = None

    class Meta:
        abstract = True

    def get_plugin_name(self):
        if self.plugin_name is None:
            raise ImproperlyConfigured("falta definir el nombre del plugin")

        return self.plugin_name

    @abstractmethod
    def config(self):
        pass

    def is_enabled(self):
        return super(KongPlugin, self).is_enabled() and self.parent.is_enabled()

    def delete_kong(self, kong_client):
        if self.parent.kong_id:
            kong_client.plugins.delete(self.get_kong_id())
        self.kong_id = None


# pylint: disable=too-few-public-methods
class KongConsumerManager(models.Manager):

    use_in_migrations = True

    anonymous_consumer_applicant = "anonymous"
    anonymous_consumer_email = "anon@anon.com"

    def create_anonymous(self, api):
        return self.create(enabled=True,
                           api=api,
                           applicant=self.anonymous_consumer_applicant,
                           contact_email=self.anonymous_consumer_email)

    def create_from_request(self, token_request):
        return self.create(enabled=True,
                           api=token_request.api,
                           applicant=token_request.applicant,
                           contact_email=token_request.contact_email)


class KongConsumer(KongObject):
    objects = KongConsumerManager()

    api = models.ForeignKey(KongApi, on_delete=models.CASCADE)
    applicant = models.CharField(max_length=100, blank=False)
    contact_email = models.EmailField(blank=False)

    class Meta:
        unique_together = ('api', 'applicant')

    def username(self):
        return '%s@%s' % (self.applicant, self.api.name)

    def create_kong(self, kong_client):
        return kong_client.consumers.create(username=self.username())

    def update_kong(self, kong_client):
        return kong_client.consumers.update(self.get_kong_id(), username=self.username())

    def delete_kong(self, kong_client):
        kong_client.consumers.delete(self.get_kong_id())
        self.kong_id = False


# pylint: disable=too-few-public-methods
class JwtCredentialManager(models.Manager):

    def create_for_consumer(self, kong_consumer):
        return self.create(enabled=True,
                           consumer=kong_consumer)


class JwtCredential(KongConsumerChildMixin, KongObject):
    objects = JwtCredentialManager()

    consumer = models.OneToOneField(KongConsumer, on_delete=models.CASCADE)
    key = models.CharField(max_length=100, null=True)
    secret = models.CharField(max_length=100, null=True)

    def create_kong(self, kong_client):
        json = self.send_create(kong_client, self.consumer, 'jwt')

        self.key = json['key']
        self.secret = json['secret']
        return json

    def _credential_endpoint(self, kong_client):
        url = urllib.parse.urljoin(kong_client.consumers.endpoint, self.consumer.get_kong_id())
        url += '/'
        url = urllib.parse.urljoin(url, 'jwt/')
        return url

    def delete_kong(self, kong_client):
        if self.consumer.kong_id is not None:
            self.send_delete(kong_client, self.consumer, 'jwt', self.get_kong_id())

        self.kong_id = None

    def update_kong(self, kong_client):
        return dict(id=self.kong_id)

    @staticmethod
    def get_kong_id_from_response(response):
        return response['id']


PENDING = "PENDING"
ACCEPTED = "ACCEPTED"
REJECTED = "REJECTED"
TOKEN_REQUEST_STATES = [
    (PENDING, 'Pendiente'),
    (ACCEPTED, 'Aceptada'),
    (REJECTED, 'Rechazada'),
]


class TokenRequest(models.Model):
    api = models.ForeignKey(KongApi, on_delete=models.CASCADE)
    applicant = models.CharField(max_length=100, blank=False)
    contact_email = models.EmailField(blank=False)
    consumer_application = models.CharField(max_length=200, blank=False)
    requests_per_day = models.IntegerField()
    state = models.CharField(default=PENDING,
                             choices=TOKEN_REQUEST_STATES,
                             max_length=20)

    def is_pending(self):
        return self.state == PENDING

    def accept(self):
        if not self.is_pending():
            raise ValidationError('only pending requests can be accepted')

        self.state = ACCEPTED
        self.save()

        self._create_consumer()

    def reject(self):
        if not self.is_pending():
            raise ValidationError('only pending requests can be rejected')

        self.state = REJECTED
        self.save()

    def _create_consumer(self):

        consumer = KongConsumer.objects.create_from_request(self)

        consumer.save()

        JwtCredential.objects.create_for_consumer(consumer).save()


class KongPluginRateLimiting(KongPlugin):
    POLICY_LOCAL = 'local'
    POLICY_CLUSTER = 'cluster'
    POLICY_CHOICES = (
        (POLICY_LOCAL, 'local'),
        (POLICY_CLUSTER, 'cluster'),
    )

    plugin_name = 'rate-limiting'
    second = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minute = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    hour = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    day = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    policy = models.CharField(max_length=12, choices=POLICY_CHOICES, default=POLICY_LOCAL)

    class Meta:
        abstract = True

    @abstractmethod
    def update_kong(self, kong_client):
        pass

    @abstractmethod
    def create_kong(self, kong_client):
        pass

    def clean(self):
        if not self.is_enabled():
            return

        config = self.config()

        if not config:
            raise ValidationError('At least one of second, '
                                  'minute, hour, or day values'
                                  ' must be provided')

        prev_k = None
        prev_v = 0
        for key, value in config.items():
            if (key != 'policy') and value < prev_v:  # it only checks numbers...
                raise ValidationError('The limit for %s cannot be lower '
                                      'than the limit for %s' % (key, prev_k))
            prev_k = key
            prev_v = value

    def config(self):
        config = OrderedDict([('second', self.second),
                              ('minute', self.minute),
                              ('hour', self.hour),
                              ('day', self.day),
                              ('policy', self.policy)])

        cleaned_config = OrderedDict()
        for key, value in config.items():
            if value:
                cleaned_config[key] = value

        return cleaned_config


class KongApiPluginRateLimiting(KongApiPlugin, KongPluginRateLimiting):
    pass


class KongApiPluginHttpLog(KongApiPlugin, KongPlugin):

    plugin_name = API_GATEWAY_LOG_PLUGIN_NAME
    api_key = models.CharField(max_length=100, blank=False, null=False)
    exclude_regex = models.CharField(max_length=100, null=False, blank=True)

    def config(self):
        return {'token': self.api_key,
                'endpoint': settings.HTTPLOG2_ENDPOINT,
                'api_data': str(self.parent.pk)}


class KongApiPluginJwt(KongApiPlugin, KongPlugin):

    plugin_name = 'jwt'
    free_tier = models.BooleanField(default=False)
    anonymous_consumer = models.OneToOneField(KongConsumer,
                                              blank=True,
                                              null=True,
                                              on_delete=models.PROTECT)

    def config(self):
        if self.free_tier and self.anonymous_consumer:
            config = {
                'anonymous': self.anonymous_consumer.get_kong_id()
            }
        else:
            config = {
                'anonymous': "",
            }

        return config


class KongApiPluginAcl(KongApiPlugin, KongPlugin):

    plugin_name = 'acl'

    def config(self):
        return {
            'whitelist': self.group_name(),
        }

    def is_enabled(self):
        try:
            return self.parent.kongapipluginjwt.is_enabled()
        except KongApiPluginJwt.DoesNotExist:
            return False

    def group_name(self):
        return self.parent.name

    @property
    def group(self):
        return AclGroup(self.group_name())


# pylint: disable=too-few-public-methods
class AclGroup(KongConsumerChildMixin):

    def __init__(self, group_name):
        self.group_name = group_name

    def add_consumer(self, kong_client, kong_consumer):
        data = dict(group=self.group_name)

        self.send_create(kong_client, kong_consumer, 'acls', data=data)


class KongConsumerPlugin(models.Model):
    parent = models.OneToOneField(KongConsumer, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def create_kong(self, kong_client):
        return kong_client.plugins.create(name=self.get_plugin_name(),
                                          consumer_id=self.parent.get_kong_id(),
                                          config=self.config())

    def update_kong(self, kong_client):
        return kong_client.plugins.update(self.get_kong_id(),
                                          consumer_id=self.parent.get_kong_id(),
                                          config=self.config())


class KongConsumerPluginRateLimiting(KongConsumerPlugin, KongPluginRateLimiting):
    pass


class KongApiPluginCors(KongApiPlugin, KongPlugin):
    plugin_name = "cors"
    origins = models.CharField(max_length=255, blank=False, null=False, default="*")

    def config(self):
        return {
            'origins': self.origins,
        }


class RootKongApi(SingletonModel, KongObject):
    upstream_url = models.URLField(blank=False)
    hosts = models.CharField(max_length=200, validators=[HostsValidator()], blank=False)

    def __str__(self):
        return "Root Kong Api"

    def create_kong(self, kong_client):
        response = kong_client.apis.create(name='root-api',
                                           uris='/?$',
                                           upstream_url=self.root_redirect_url(),
                                           hosts=self.hosts)
        self.kong_id = response.id
        return response

    def update_kong(self, kong_client):
        return kong_client.apis.update(self.get_kong_id(),
                                       uris='/?$',
                                       upstream_url=self.root_redirect_url(),
                                       hosts=self.hosts)

    def delete_kong(self, kong_client):
        kong_client.apis.delete(self.get_kong_id())
        self.kong_id = None

    def root_redirect_url(self):
        return settings.KONG_TRAFFIC_URL + reverse('root-redirect')


class KongApiHistoricHits(models.Model):
    kong_id = models.OneToOneField(KongApi, on_delete=models.CASCADE)
    accumulated_hits = models.IntegerField(default=0)

    def __str__(self):
        return "Consultas históricas"


@receiver(post_save, sender=KongApi)
def re_enable_kong_plugins(created, instance, *_, **__):
    if not created:
        for plugin in instance.plugins:
            plugin.save()


@receiver(post_save, sender=KongApi)
def init_acl_plugin(created, instance, *_, **__):
    if created:
        KongApiPluginAcl(parent=instance).save()


@receiver(post_save, sender=KongApiPluginJwt)
def init_anon_user(created, instance, *_, **__):
    if created:
        consumer = KongConsumer.objects.create_anonymous(
            api=instance.parent,
        )
        consumer.save()

        instance.anonymous_consumer = consumer
        instance.save()


@receiver(pre_save, sender=KongApiPluginJwt)
def manage_acl(instance, *_, **__):
    instance.parent.kongapipluginacl.save()


@receiver(post_save, sender=KongConsumer)
def assign_acl_group(created, instance, *_, **__):
    if created:
        instance.api.kongapipluginacl.group.add_consumer(kong_client_using_settings(), instance)


@receiver(pre_save, sender=KongApi)
@receiver(pre_save, sender=KongApiPluginRateLimiting)
@receiver(pre_save, sender=KongApiPluginHttpLog)
@receiver(pre_save, sender=KongApiPluginJwt)
@receiver(pre_save, sender=KongConsumer)
@receiver(pre_save, sender=JwtCredential)
@receiver(pre_save, sender=KongApiPluginAcl)
@receiver(pre_save, sender=KongConsumerPluginRateLimiting)
@receiver(pre_save, sender=KongApiPluginCors)
@receiver(pre_save, sender=RootKongApi)
def manage_kong_on_save(instance, *_, **__):
    instance.manage_kong(kong_client_using_settings())


@receiver(pre_delete, sender=KongApi)
@receiver(pre_delete, sender=KongConsumer)
@receiver(pre_delete, sender=RootKongApi)
def delete_kong_on_delete(instance, *_, **__):
    instance.delete_kong(kong_client_using_settings())
