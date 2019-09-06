from django.db import models
from solo.models import SingletonModel


class GoogleAnalyticsSettings(SingletonModel):
    ga_id = models.CharField(max_length=100, blank=True, default='',
                             verbose_name='Google analytics ID')
    max_timeout = models.IntegerField(default=10, verbose_name='session timeout in minutes')

    def __str__(self):
        return 'GoogleAnalyticsSettings'
