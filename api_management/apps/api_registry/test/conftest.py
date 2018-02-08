import string
import pytest
from faker import Faker
from faker.providers import BaseProvider

from ..models import ApiData


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
        return "".join(chars)


@pytest.fixture()
def faker():
    a_faker = Faker()
    a_faker.add_provider(CustomInfoProvider)
    return a_faker


@pytest.fixture()
def api_data(faker):  # pylint: disable=redefined-outer-name
    return ApiData(name=faker.api_name(),
                   upstream_url=faker.url(),
                   uri=faker.api_path(),
                   kong_id=None)


@pytest.fixture()
def kong_client(faker, mocker):  # pylint: disable=redefined-outer-name

    def create_side_effect(*args, **kwargs):  # pylint: disable=unused-argument
        return {'id': faker.kong_id()}

    stub = mocker.stub(name='kong_client_stub')
    stub.create = mocker.stub(name='kong_client_create_stub')
    stub.create.side_effect = create_side_effect
    stub.update = mocker.stub(name='kong_client_update_stub')
    stub.delete = mocker.stub(name='kong_client_delete_stub')
    return stub
