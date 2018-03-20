from urllib.parse import parse_qsl
import requests_mock
from api_management.apps.analytics.models import send_analytics


def test_send_analytics(query):
    with requests_mock.mock() as rmock:
        # Setup
        rmock.post(requests_mock.ANY, status_code=200)
        tracking_id = 'UA-XXXXXXXXX-Y'

        # Exercise
        send_analytics(query, tracking_id)

        # Verify
        history = rmock.request_history
        assert len(history) == 1

        request = history[0]
        assert request.method == 'POST'
        assert request.url == 'http://www.google-analytics.com/collect'

        expected_data = {'v': 1,  # Protocol Version
                         'cid': query.id,  # Client ID
                         'tid': tracking_id,  # Tracking ID
                         't': 'pageview',  # Hit Type
                         'uip': query.ip_address,  # User IP override
                         'dh': query.host,  # Document HostName
                         'dp': query.uri,  # Document Path
                         'cd1': query.querystring,  # Custom Dimention
                         'srt': query.request_time,  # Server Response Time
                         'cm1': query.start_time,  # Custom Metric
                         'cm2': query.status_code,  # Custom Metric
                         'cd3': query.api_data.name,
                         'cm3': query.api_data.pk}

        for key, val in expected_data.items():
            expected_data[key] = str(val)

        assert dict(parse_qsl(request.text)) == expected_data
