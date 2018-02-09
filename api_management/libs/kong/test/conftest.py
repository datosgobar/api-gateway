import string
from http.client import OK, CREATED, CONFLICT, NO_CONTENT
from faker import Faker
from faker.providers import BaseProvider
import pytest

from django.conf import settings

from ..client import APIAdminClient


API_URL = settings.KONG_ADMIN_URL


class CustomInfoProvider(BaseProvider):

    def api_name(self):
        return self.generator.name().replace(' ', '')

    def api_path(self):
        path = self.generator.uri_path()
        if not path.startswith('/'):
            path = '/%s' % path
        return path

    def kong_id(self, grouping=(8, 4, 4, 4, 12),
                valid_elements=tuple(string.ascii_lowercase + string.digits)):
        """
            Generates a random kong_id
            Example: "14656344-9e38-4315-8ae2-c23551ea3b9d"
        :return:
        """
        chars = []
        for group in grouping:
            chars += self.random_sample(elements=valid_elements, length=group)
            chars += "-"
        chars.pop()
        return "".join(chars)


@pytest.fixture()
def fake():
    a_faker = Faker()
    a_faker.add_provider(CustomInfoProvider)
    return a_faker


names = []


@pytest.fixture
def created_names():
    return names


@pytest.fixture
def already_exists_response(mocker):
    response = mocker.stub(name='response_stub')
    response.status_code = CONFLICT
    response.content = "name already exists"
    return response


@pytest.fixture
def missing_fields_response(mocker):
    response = mocker.stub(name='response_stub')
    response.status_code = 400
    response.content = "missing parameter"
    return response


def valid_fields(dictionary):
    required_fields = ['uris', 'hosts']
    valid = False
    for key in dictionary:
        valid = valid or (key in required_fields and dictionary[key] is not None)
    return valid


@pytest.fixture
def session_stub(mocker, fake, created_names, already_exists_response, missing_fields_response):
    def post_side_effect(url, **kwargs):
        if kwargs['data']['name'] in created_names:
            return already_exists_response

        if not valid_fields(kwargs['data']):
            return missing_fields_response

        created_names.append(kwargs['data']['name'])
        response = mocker.stub(name='response_stub')
        response.status_code = CREATED
        kong_id = fake.kong_id()
        id_dict = {'id': kong_id}
        response.json = lambda: {**id_dict, **kwargs['data']}
        return response

    def patch_side_effect(url, **kwargs):
        response = mocker.stub(name='response_stub')
        response.status_code = OK
        response.json = lambda: kwargs['data']
        return response

    def get_side_effect(url, **kwargs):
        response = mocker.stub(name='response_stub')
        response.status_code = OK
        apis = []
        for name in created_names:
            apis.append({'name': name})
        response.json = lambda: {'data': apis}
        return response

    def delete_side_effect(url, **kwargs):
        response = mocker.stub(name='response_stub')
        response.status_code = NO_CONTENT
        return response

    stub = mocker.stub(name='session_stub')
    stub.post = mocker.stub(name='session_post_stub')
    stub.post.side_effect = post_side_effect
    stub.patch = mocker.stub(name='session_patch_stub')
    stub.patch.side_effect = patch_side_effect
    stub.delete = mocker.stub(name='session_delete_stub')
    stub.delete.side_effect = delete_side_effect
    stub.get = mocker.stub(name='session_get_stub')
    stub.get.side_effect = get_side_effect
    return stub


@pytest.fixture
def requests_stub(mocker, session_stub):
    stub = mocker.stub(name='requests_stub')
    stub.session = mocker.stub(name='requests_session_stub')
    stub.session.side_effect = lambda **kwargs: session_stub
    return stub


@pytest.fixture
def kong(requests_stub):
    names.clear()
    return APIAdminClient(API_URL, requests_module=requests_stub)


@pytest.fixture
def kong_admin_url():
    return API_URL
