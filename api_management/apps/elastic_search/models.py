from elasticsearch_dsl import Keyword, Date, Integer, Ip, Text, Float, Document

# pylint: disable=too-few-public-methods
from api_management.apps.analytics.models import generate_api_session_id


class QueryIndex(Document):
    ip_address = Ip()
    host = Keyword()
    uri = Keyword()
    querystring = Text()
    start_time = Date()
    request_time = Float()
    status_code = Integer()
    api_name = Keyword()
    user_agent = Text()
    token = Keyword()
    x_source = Keyword()
    request_method = Keyword()
    api_session_id = Keyword()

    class Index:
        name = 'query-index'


def index_query(query):
    obj = QueryIndex(
        meta={'id': query.id},
        ip_address=query.ip_address,
        host=query.host,
        uri=query.uri,
        querystring=query.querystring,
        start_time=query.start_time,
        request_time=query.request_time,
        status_code=query.status_code,
        api_name=query.api_data.name,
        user_agent=query.user_agent,
        token=query.token,
        x_source=query.x_source,
        request_method=query.request_method,
        api_session_id=generate_api_session_id(query),
    )
    obj.save()
    return obj.to_dict(include_meta=True)
