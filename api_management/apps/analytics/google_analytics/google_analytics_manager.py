import hashlib
import re
import uuid

import requests
from django.conf import settings
from redis import Redis

from api_management.apps.analytics.google_analytics.google_analytics_settings \
    import GoogleAnalyticsSettings


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

        if not self.redis_client.exists(query.api_session_id()):
            data['sc'] = 'start'  # this request starts a new session

        min_to_timeout = GoogleAnalyticsSettings.get_solo().max_timeout
        self.redis_client.append(query.api_session_id(), 'start')
        self.redis_client.expire(query.api_session_id(), min_to_timeout*60)

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


def is_options_request(query):
    return query.request_method == 'OPTIONS'
