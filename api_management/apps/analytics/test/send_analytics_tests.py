import hashlib
import uuid
from unittest.mock import MagicMock
from urllib.parse import parse_qsl

import pytest
import requests_mock
from django.conf import settings
from redis import Redis


def test_send_analytics(ga_manager, tracking_id, query):
    token = query.ip_address + query.user_agent

    payload_generation = expected_data_with_session
    execute_and_verify_analytics(ga_manager, query, token, tracking_id, payload_generation)


def test_send_analytics_with_token(ga_manager, tracking_id, query):
    token = "a36c3049b36249a3c9f8891cb127243c"
    query.token = token

    payload_generation = expected_data_with_session
    execute_and_verify_analytics(ga_manager, query, token, tracking_id, payload_generation)


# pylint: disable=invalid-name
def test_send_analytics_without_session_param(ga_manager, tracking_id, query):
    token = query.ip_address + query.user_agent
    set_up_redis(query)

    payload_generation = generate_default_payload
    execute_and_verify_analytics(ga_manager, query, token, tracking_id, payload_generation)


MATCHING_REGEX_URI_PAIRS = [('regex', '/api/regex/test/'),
                            ('static', '/api/static/resource'),
                            ('media', '/media')]


#  pylint: disable=invalid-name
@pytest.mark.parametrize("regex,uri", MATCHING_REGEX_URI_PAIRS)
def test_if_exclude_regex_matches_query_uri_send_analyitics_you_must_not(ga_manager, query,
                                                                         regex, uri, httplogdata):
    exercise_manage_query(ga_manager, query, regex, uri, httplogdata)

    # Verify
    ga_manager.send_analytics.assert_not_called()


NON_MATCHING_REGEX_URI_PAIRS = [('', '/path/'),
                                ('no-match', '/path/'),
                                ('no-match', '')]


#  pylint: disable=invalid-name
@pytest.mark.parametrize("regex,uri", NON_MATCHING_REGEX_URI_PAIRS)
def test_if_exclude_regex_does_not_matches_query_uri_send_analyitics_you_must(ga_manager, query,
                                                                              regex, uri,
                                                                              httplogdata):
    exercise_manage_query(ga_manager, query, regex, uri, httplogdata)

    # Verify
    ga_manager.send_analytics.assert_called_once_with(query)


# pylint: disable=invalid-name
def test_exclude_analytics_for_options_request(ga_manager, query):
    ga_manager.manage_query = MagicMock()

    query.request_method = 'OPTIONS'
    ga_manager.prepare_send_analytics(True, query)
    ga_manager.manage_query.assert_not_called()


#  Auxiliary functions:
def set_up_redis(query):
    redis_client = Redis(host=settings.RQ_QUEUES["default"]["HOST"],
                         port=settings.RQ_QUEUES["default"]["PORT"])
    redis_client.append(query.api_session_id(), 'start')
    redis_client.expire(query.api_session_id(), 10)


def exercise_manage_query(ga_manager, query, regex, uri, httplogdata):
    # Setup
    ga_manager.send_analytics = MagicMock()
    httplogdata.exclude_regex = regex
    query.api_data.httplogdata = httplogdata
    query.uri = uri

    # Exercise
    ga_manager.manage_query(query)


def generate_default_payload(token, tracking_id, query):
    expected_cid = hashlib.sha1(token.encode()).digest()
    expected_cid = str(uuid.UUID(bytes=expected_cid[:16]))
    return {'v': 1,  # Protocol Version
            'cid': expected_cid,  # Client ID
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
            'cm3': query.api_data.pk,
            'ua': query.user_agent}


def expected_data_with_session(token, tracking_id, query):
    payload = generate_default_payload(token, tracking_id, query)
    payload['sc'] = 'start'
    return payload


def assert_request_to_google_analytics(request):
    assert request.method == 'POST'
    assert request.url == 'http://www.google-analytics.com/collect'


def execute(rmock, ga_manager, query):
    # Setup
    rmock.post(requests_mock.ANY, status_code=200)

    # Exercise
    ga_manager.send_analytics(query)

    # Verify
    history = rmock.request_history
    assert len(history) == 1
    request = history[0]
    assert_request_to_google_analytics(request)
    return request


def execute_and_verify_analytics(ga_manager, query, token, tracking_id, payload_generation):
    with requests_mock.mock() as rmock:
        request = execute(rmock, ga_manager, query)
        expected_result = payload_generation(token, tracking_id, query)

        for key, val in expected_result.items():
            expected_result[key] = str(val)

        assert dict(parse_qsl(request.text)) == expected_result
