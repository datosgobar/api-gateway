from django.db import models
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
