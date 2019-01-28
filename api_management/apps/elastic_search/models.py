from elasticsearch_dsl import Keyword, Date, Integer, Ip, Text, Float, Document


# pylint: disable=too-few-public-methods
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
