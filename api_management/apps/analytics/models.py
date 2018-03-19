import requests

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from api_management.apps.api_registry.models import ApiData


class Query(models.Model):
    """Registro de queries exitosas, guardadas con el propósito de analytics"""
    ip_address = models.CharField(max_length=200, null=True)
    host = models.TextField()
    uri = models.TextField()
    querystring = models.TextField(default="", blank=True)
    start_time = models.DateTimeField()
    request_time = models.DecimalField(max_digits=20, decimal_places=15)
    status_code = models.IntegerField(blank=True, null=True)
    api_data = models.ForeignKey(ApiData, blank=True, null=True, on_delete=models.PROTECT)

    class Meta:  # pylint: disable=too-few-public-methods
        verbose_name = _("query")
        verbose_name_plural = _("queries")

    def __str__(self):
        return 'Query at %s: %s' % (self.start_time, self.uri)


@receiver(post_save, sender=Query)
def send_analytics(**kwargs):
    query = kwargs['instance']
    tracking_id = settings.ANALYTICS_TID

    data = {'v': 1,                     # Protocol Version
            'cid': query.id,            # Client ID
            'tid': tracking_id,         # Tracking ID
            'uip': query.ip_address,    # User IP override
            't': 'pageview',            # Hit Type
            'dh': query.host,           # Document HostName
            'dp': query.uri,            # Document Path
            'cd1': query.querystring,   # Custom Dimention
            'cm1': query.start_time,    # Custom Metric
            'srt': query.request_time,  # Server Response Time
            'cm2': query.status_code,   # Custom Metric
            'cd3': query.api_data.name,
            'cm3': query.api_data.pk}

    response = requests.post('http://www.google-analytics.com/collect', data=data)

    if not response.ok:
        raise ConnectionError(response.content)
