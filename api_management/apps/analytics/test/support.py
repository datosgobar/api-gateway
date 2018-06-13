from urllib.parse import parse_qsl, urlparse

from faker import Faker

from api_management.libs.providers.providers import CustomInfoProvider


def custom_faker():
    # Custom Fake
    a_faker = Faker()
    a_faker.add_provider(CustomInfoProvider)
    return a_faker


def dict_from_querystring(querystring):
    return dict(parse_qsl(
        urlparse("https://example.com/?%s" % querystring).query,
        keep_blank_values=True
    ))


def query_dict_response(query_dict):
    response = query_dict.copy()
    response['params'] = dict_from_querystring(query_dict['querystring'])
    return response
