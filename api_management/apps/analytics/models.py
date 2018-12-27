import abc
import hashlib
import re
from urllib.parse import parse_qsl, urlparse

import uuid
from datetime import date
import requests
from dateutil import relativedelta
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from redis import Redis
from solo.models import SingletonModel

from api_management.apps.api_registry.models import KongApi


def next_day_of(a_day):
    return a_day + relativedelta.relativedelta(days=1)


class Query(models.Model):
    """Registro de queries exitosas, guardadas con el propósito de analytics"""
    ip_address = models.CharField(max_length=200, null=True)
    host = models.TextField()
    uri = models.TextField()
    querystring = models.TextField(default="", blank=True)
    start_time = models.DateTimeField(db_index=True)
    request_time = models.DecimalField(max_digits=30, decimal_places=25)
    status_code = models.IntegerField(blank=True, null=True)
    api_data = models.ForeignKey(KongApi, blank=True, null=True, on_delete=models.PROTECT)
    user_agent = models.TextField()
    token = models.CharField(max_length=200, null=True)
    x_source = models.TextField(default="", null=True, blank=True)
    request_method = models.CharField(max_length=10, null=True, default="", blank=True)

    class Meta:  # pylint: disable=too-few-public-methods
        verbose_name = _("query")
        verbose_name_plural = _("queries")

    def params(self):
        return dict(parse_qsl(
            urlparse("https://example.com/?%s" % self.querystring).query,
            keep_blank_values=True
        ))

    def __str__(self):
        return 'Query at %s: %s' % (self.start_time, self.uri)


class GoogleAnalyticsSettings(SingletonModel):
    ga_id = models.CharField(max_length=100, blank=True, default='',
                             verbose_name='Google analytics ID')

    def __str__(self):
        return 'GoogleAnalyticsSettings'


def is_options_request(query):
    return query.request_method == 'OPTIONS'


def generate_api_session_id(query):
    return query.ip_address + query.api_data.name + query.user_agent


class GoogleAnalyticsManager:

    @classmethod
    def using_settings(cls):
        ga_id = ''
        ga_settings = GoogleAnalyticsSettings.objects.first()
        if ga_settings is not None:
            ga_id = ga_settings.ga_id

        return cls(tracking_id=ga_id)

    def __init__(self, tracking_id):
        self.session = requests.session()
        self.tracking_id = tracking_id
        self.redis_client = Redis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT)

    @staticmethod
    @receiver(post_save, sender=Query)
    def prepare_send_analytics(created, instance, **_):
        if (not is_options_request(instance)) and created:
            query = instance

            GoogleAnalyticsManager.using_settings().manage_query(query)

    def manage_query(self, query):
        regex = query.api_data.kongapipluginhttplog.exclude_regex
        if not regex \
                or re.search(regex, query.uri) is None:
            self.send_analytics(query)

    def generate_payload(self, cid, query):
        data = {'v': 1,  # Protocol Version
                'cid': cid,  # Client ID
                'tid': self.tracking_id,  # Tracking ID
                'uip': query.ip_address,  # User IP override
                't': 'pageview',  # Hit Type
                'dh': query.host,  # Document HostName
                'dp': query.uri,  # Document Path
                'cd1': query.querystring,  # Custom Dimention
                'cm1': query.start_time,  # Custom Metric
                'srt': query.request_time,  # Server Response Time
                'cm2': query.status_code,  # Custom Metric
                'cd3': query.api_data.name,
                'cm3': query.api_data.pk,
                'ua': query.user_agent}

        api_session_id = generate_api_session_id(query)

        if not self.redis_client.exists(api_session_id):
            data['sc'] = 'start'  # this request starts a new session

        min_to_timeout = ApiSessionSettings.get_solo().max_timeout
        self.redis_client.append(api_session_id, 'start')
        self.redis_client.expire(api_session_id, min_to_timeout*60)

        return data

    def send_analytics(self, query):
        if query.token is None:
            cid = query.ip_address + query.user_agent
        else:
            cid = query.token

        cid = hashlib.sha1(cid.encode()).digest()
        cid = str(uuid.UUID(bytes=cid[:16]))
        data = self.generate_payload(cid, query)

        response = self.session.post('http://www.google-analytics.com/collect', data=data)
        if not response.ok:
            raise ConnectionError(response.content)


class CsvFile(models.Model):
    TYPE_ANALYTICS = 'analytics'
    TYPE_INDICATORS = 'indicators'
    TYPE_CHOICES = (
        (TYPE_ANALYTICS, 'analytics'),
        (TYPE_INDICATORS, 'indicators'),
    )

    api_name = models.CharField(max_length=30, null=False, blank=False)
    file_name = models.CharField(max_length=100, null=False, blank=False)
    file = models.FileField(upload_to='media')
    type = models.CharField(max_length=30, null=False, blank=False, choices=TYPE_CHOICES)


class CsvGeneratorTaskLogger(models.Model):
    created_at = models.DateTimeField()
    logs = models.TextField()

    class Meta:
        abstract = True

    def log_success(self, api_name, analytics_date):
        self.logs += self.success_task_log(api_name, analytics_date)
        self.save()

    def log_error(self, api_name, analytics_date, exception):
        self.logs += self.error_task_log(api_name, exception, analytics_date)
        self.save()

    @abc.abstractmethod
    def success_task_log(self, api_name, analytics_date):
        raise NotImplementedError

    @abc.abstractmethod
    def error_task_log(self, api_name, exception, analytics_date=None):
        raise NotImplementedError


class CsvAnalyticsGeneratorTask(CsvGeneratorTaskLogger):

    def success_task_log(self, api_name, analytics_date):
        return "({api_name}) Csv de analytics generado correctamente para el día {date}.\n" \
            .format(api_name=api_name, date=analytics_date)

    def error_task_log(self, api_name, exception, analytics_date=None):
        return "({api_name}) Error generando csv de analytics para el día {value}: {exception}\n" \
            .format(api_name=api_name, value=analytics_date, exception=exception)


class IndicatorCsvGeneratorTask(CsvGeneratorTaskLogger):

    def success_task_log(self, api_name, analytics_date):
        return "({api_name}) Csv de indicadores generado correctamente.\n" \
            .format(api_name=api_name)

    def error_task_log(self, api_name, exception, analytics_date=None):
        return "({api_name}) Error generando csv de indicadores: {exception}\n" \
            .format(api_name=api_name, exception=exception)


class ApiSessionSettings(SingletonModel):
    max_timeout = models.IntegerField(default=10, verbose_name='Timeout in minutes')

    def __str__(self):
        return 'ApiSessionSettings'


class IndicatorMetricsRow(models.Model):
    api_name = models.CharField(max_length=100, blank=False, null=False)
    date = models.DateTimeField(blank=True, null=True)
    all_queries = models.IntegerField(blank=True, null=True)
    all_mobile = models.IntegerField(blank=True, null=True)
    all_not_mobile = models.IntegerField(blank=True, null=True)
    total_users = models.IntegerField(blank=True, null=True)


class IndicatorMetricsCalculator:

    def __init__(self, api_name):
        self.api_name = api_name

    def is_mobile(self, user_agent):
        return "Mobile" in user_agent or \
               "Android" in user_agent or \
               "iPhone" in user_agent or \
               "Slackbot" in user_agent

    def indicator_row_content(self, queries):
        unique_session_ids = set()
        total_mobile = 0
        total_not_mobile = 0

        for query in queries:
            unique_session_ids.add(generate_api_session_id(query))

            if self.is_mobile(query.user_agent):
                total_mobile = total_mobile + 1
            else:
                total_not_mobile = total_not_mobile + 1

        return {'total': total_mobile + total_not_mobile,
                'total_mobile': total_mobile,
                'total_not_mobile': total_not_mobile,
                'total_unique_users': len(unique_session_ids)}

    def first_query_time(self):
        query_time = Query.objects.first().start_time
        last_row = IndicatorMetricsRow.objects.filter(api_name=self.api_name).last()
        if last_row is not None:
            query_time = last_row.date

        return query_time

    def calculate(self):
        query_time = self.first_query_time()

        while query_time.date() < date.today():
            queries = self.all_queries(query_time)
            total_counts = self.indicator_row_content(queries)

            indicator_row = IndicatorMetricsRow(api_name=self.api_name)
            indicator_row.date = query_time.date()
            indicator_row.all_queries = total_counts.get('total')
            indicator_row.all_mobile = total_counts.get('total_mobile')
            indicator_row.all_not_mobile = total_counts.get('total_not_mobile')
            indicator_row.total_users = total_counts.get('total_unique_users')
            indicator_row.save()
            query_time = next_day_of(query_time)

    def all_queries(self, query_time):
        return Query.objects.filter(api_data__name=self.api_name,
                                    start_time__gte=query_time,
                                    start_time__lt=next_day_of(query_time))\
                            .exclude(request_method='OPTIONS')
