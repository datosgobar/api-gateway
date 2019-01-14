from datetime import datetime

from dateutil import relativedelta

from api_management.apps.analytics.metrics_calculator import IndicatorMetricsCalculator
from api_management.apps.analytics.models import Query
from api_management.apps.analytics.test.user_agents import user_agents


def test_is_mobile():
    calculator = IndicatorMetricsCalculator(api_name='foo')

    assert calculator.is_mobile(user_agents.get('linux')) is False
    assert calculator.is_mobile(user_agents.get('safari_ios'))
    assert calculator.is_mobile(user_agents.get('android_firefox'))
    assert calculator.is_mobile(user_agents.get('slack_browser'))


def test_indicator_row_content(kong_api):
    queries = [Query(ip_address="192.168.1.1", host="foo", uri="/series", querystring="?foo=1",
                     start_time=datetime.now(), request_time=1, status_code=200,
                     api_data=kong_api, user_agent=user_agents.get('safari_ios'), token="123",
                     request_method="POST")]

    calculator = IndicatorMetricsCalculator(api_name='foo')
    row_contents = calculator.indicator_row_content(queries)

    assert row_contents.get('total') == 1
    assert row_contents.get('total_mobile') == 1
    assert row_contents.get('total_not_mobile') == 0
    assert row_contents.get('total_unique_users') == 1


def test_indicator_last_30(kong_api):
    query = Query(ip_address="192.168.1.1", host="foo", uri="/series", querystring="?foo=1",
                  start_time=datetime.now(), request_time=1, status_code=200,
                  api_data=kong_api, user_agent=user_agents.get('safari_ios'), token="123",
                  request_method="POST")

    calculator = IndicatorMetricsCalculator(api_name='foo')
    assert calculator.api_session_id_last_days(query, 30) is not None
    assert calculator.api_session_id_last_days(query, 90) is not None
    assert calculator.api_session_id_last_days(query, 180) is not None


def test_indicator_last_90(kong_api):
    query = Query(ip_address="192.168.1.1", host="foo", uri="/series", querystring="?foo=1",
                  start_time=datetime.now() - relativedelta.relativedelta(days=90),
                  request_time=1, status_code=200,
                  api_data=kong_api, user_agent=user_agents.get('safari_ios'), token="123",
                  request_method="POST")

    calculator = IndicatorMetricsCalculator(api_name='foo')
    assert calculator.api_session_id_last_days(query, 30) is None
    assert calculator.api_session_id_last_days(query, 90) is not None
    assert calculator.api_session_id_last_days(query, 180) is not None
