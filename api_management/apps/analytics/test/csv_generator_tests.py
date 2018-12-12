from datetime import datetime

from api_management.apps.analytics.csv_generator import is_mobile, indicator_row_content
from api_management.apps.analytics.models import Query
from api_management.apps.analytics.test.user_agents import user_agents


def test_is_mobile():
    assert is_mobile(user_agents.get('linux')) is False
    assert is_mobile(user_agents.get('safari_ios'))
    assert is_mobile(user_agents.get('android_firefox'))
    assert is_mobile(user_agents.get('slack_browser'))


def test_indicator_row_content(kong_api):
    queries = [Query(ip_address="192.168.1.1", host="foo", uri="/series", querystring="?foo=1",
                     start_time=datetime.now(), request_time=1, status_code=200,
                     api_data=kong_api, user_agent=user_agents.get('safari_ios'), token="123",
                     request_method="POST")]

    row_contents = indicator_row_content(queries)

    assert row_contents.get('total') == 1
    assert row_contents.get('total_mobile') == 1
    assert row_contents.get('total_not_mobile') == 0
    assert row_contents.get('total_unique_users') == 1
