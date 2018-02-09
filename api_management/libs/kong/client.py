import os
from urllib.parse import urljoin
# pylint: disable=no-name-in-module
from http.client import OK, CREATED, CONFLICT, NO_CONTENT, \
        NOT_FOUND, INTERNAL_SERVER_ERROR

import six
import requests

from .utils import add_url_params, assert_dict_keys_in, ensure_trailing_slash
from .exceptions import ConflictError, ServerError

# Minimum interval between requests (measured in seconds)
KONG_MINIMUM_REQUEST_INTERVAL = float(os.getenv('KONG_MINIMUM_REQUEST_INTERVAL', 0))

# Whether or not to reuse connections after a request (1 = true, otherwise false)
KONG_REUSE_CONNECTIONS = int(os.getenv('KONG_REUSE_CONNECTIONS', '1')) == 1


def get_default_kong_headers():
    headers = {}
    if not KONG_REUSE_CONNECTIONS:
        headers.update({'Connection': 'close'})
    return headers


def raise_response_error(response, exception_class=None):
    exception_class = exception_class or ValueError
    assert issubclass(exception_class, BaseException)
    raise exception_class(response.content)


INVALID_FIELD_ERROR_TEMPLATE = '%r is not a valid field. Allowed fields: %r'


class RestClient(object):
    def __init__(self, api_url, headers=None, requests_module=requests):
        self.requests_module = requests_module
        self.api_url = api_url
        self.headers = headers
        self._session = None

    def destroy(self):
        self.api_url = None
        self.headers = None

        if self._session is not None:
            self._session.close()
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self._session = self.requests_module.session()
            if KONG_MINIMUM_REQUEST_INTERVAL > 0:
                self._session.mount(self.api_url, None)
        elif not KONG_REUSE_CONNECTIONS:
            self._session.close()
            self._session = None
            return self.session
        return self._session

    def get_headers(self, **headers):
        result = {}
        result.update(self.headers)
        result.update(headers)
        return result

    def get_url(self, *path, **query_params):
        # Never use str, unless in some very specific cases,
        # like in compatibility layers! Fixed for you.
        path = [six.text_type(p) for p in path]
        url = ensure_trailing_slash(urljoin(self.api_url, '/'.join(path)))
        return add_url_params(url, query_params)


class APIAdminClient(RestClient):
    def __init__(self, api_url, requests_module=requests):
        super(APIAdminClient, self).__init__(api_url,
                                             headers=get_default_kong_headers(),
                                             requests_module=requests_module)

    # pylint: disable=too-many-arguments
    def create(self, upstream_url, name=None, hosts=None, uris=None, strip_uri=None,
               preserve_host=None):
        response = self.session.post(self.get_url('apis'), data={
            'name': name,
            'hosts': hosts,
            'uris': uris,
            'strip_uri': strip_uri,
            'preserve_host': preserve_host,
            'upstream_url': upstream_url
        }, headers=self.get_headers())

        if response.status_code == CONFLICT:
            raise_response_error(response, ConflictError)
        elif response.status_code == INTERNAL_SERVER_ERROR:
            raise_response_error(response, ServerError)
        elif response.status_code != CREATED:
            raise_response_error(response, ValueError)

        return response.json()

    def update(self, name_or_id, **fields):
        assert_dict_keys_in(
            fields, ['name', 'hosts', 'uris', 'upstream_url', 'strip_uri', 'preserve_host'],
            INVALID_FIELD_ERROR_TEMPLATE)

        # Explicitly encode on beforehand before passing to requests!
        fields = dict((k, v) if isinstance(v, six.text_type)
                      else v for k, v in fields.items())

        response = self.session.patch(self.get_url('apis', name_or_id),
                                      data=dict(**fields), headers=self.get_headers())

        if response.status_code == INTERNAL_SERVER_ERROR:
            raise_response_error(response, ServerError)
        elif response.status_code != OK:
            raise_response_error(response, ValueError)

        return response.json()

    def delete(self, name_or_id):
        response = self.session.delete(self.get_url('apis', name_or_id), headers=self.get_headers())

        if response.status_code not in (NO_CONTENT, NOT_FOUND):
            raise ValueError('Could not delete API (status: %s): %s'
                             % (response.status_code, name_or_id))

    def list(self, size=100, offset=None, **filter_fields):
        assert_dict_keys_in(filter_fields, ['id', 'name',
                                            'upstream_url',
                                            'retries'], INVALID_FIELD_ERROR_TEMPLATE)

        query_params = filter_fields
        query_params['size'] = size

        if offset:
            query_params['offset'] = offset

        url = self.get_url('apis', **query_params)
        response = self.session.get(url, headers=self.get_headers())

        if response.status_code == INTERNAL_SERVER_ERROR:
            raise_response_error(response, ServerError)
        elif response.status_code != OK:
            raise_response_error(response, ValueError)

        return response.json()

    def count(self):
        response = self.session.get(self.get_url('apis'), headers=self.get_headers())

        if response.status_code == INTERNAL_SERVER_ERROR:
            raise_response_error(response, ServerError)

        result = response.json()
        amount = result.get('total', len(result.get('data')))

        return amount
