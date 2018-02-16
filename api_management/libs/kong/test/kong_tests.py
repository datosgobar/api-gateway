import pytest

from ..exceptions import ConflictError
from ..utils import add_url_params


def test_create(fake, kong, kong_admin_url, session_stub):
    # Setup
    url = fake.url()
    name = fake.api_name()
    host = fake.domain_name()

    # Exercise
    kong.create(upstream_url=url, name=name, hosts=host)

    # Verify
    session_stub.post.assert_called_once_with(kong_admin_url + 'apis/',
                                              headers={},
                                              data={'name': name,
                                                    'hosts': host,
                                                    'uris': None,
                                                    'strip_uri': None,
                                                    'preserve_host': None,
                                                    'upstream_url': url})


def test_create_conflict_name(fake, kong, session_stub, kong_admin_url):
    # Setup
    url = fake.url()
    name = fake.api_name()
    host = fake.domain_name()

    new_url = fake.url()
    new_host = fake.domain_name()

    # Exercise
    kong.create(upstream_url=url, name=name, hosts=host)

    with pytest.raises(ConflictError):
        kong.create(upstream_url=new_url, name=name, hosts=new_host)

    # Verify
    session_stub.post.assert_called_with(kong_admin_url + 'apis/',
                                         headers={},
                                         data={'name': name,
                                               'hosts': new_host,
                                               'uris': None,
                                               'strip_uri': None,
                                               'preserve_host': None,
                                               'upstream_url': new_url})


def test_create_same_public_host(fake, kong, session_stub, kong_admin_url):
    # Setup
    url = fake.url()
    name = fake.api_name()
    host = fake.domain_name()

    new_name = fake.api_name()
    new_url = fake.url()

    # Exercise
    kong.create(upstream_url=url, name=name, hosts=host)

    kong.create(upstream_url=new_url, name=new_name, hosts=host)

    # Verify
    session_stub.post.assert_any_call(kong_admin_url + 'apis/',
                                      headers={},
                                      data={'name': name,
                                            'hosts': host,
                                            'uris': None,
                                            'strip_uri': None,
                                            'preserve_host': None,
                                            'upstream_url': url})
    session_stub.post.assert_called_with(kong_admin_url + 'apis/',
                                         headers={},
                                         data={'name': new_name,
                                               'hosts': host,
                                               'uris': None,
                                               'strip_uri': None,
                                               'preserve_host': None,
                                               'upstream_url': new_url})


# pylint: disable=invalid-name
def test_create_missing_hosts_and_uris(fake, kong):
    # Exercise
    with pytest.raises(ValueError):
        kong.create(name=fake.api_name(), upstream_url=fake.url())


def test_create_missing_hosts(fake, kong, session_stub, kong_admin_url):
    # Setup
    name = fake.api_name()
    uri = fake.api_path()
    url = fake.url()

    # Exercise
    kong.create(name=name, upstream_url=url, uris=uri)

    # Verify
    session_stub.post.assert_called_with(kong_admin_url + 'apis/',
                                         headers={},
                                         data={'name': name,
                                               'hosts': None,
                                               'uris': uri,
                                               'strip_uri': None,
                                               'preserve_host': None,
                                               'upstream_url': url})


def test_create_missing_uris(fake, kong, session_stub, kong_admin_url):
    # Setup
    name = fake.api_name()
    url = fake.url()
    host = fake.domain_name()

    # Exercise
    kong.create(name=name, upstream_url=url, hosts=host)

    # Verify
    session_stub.post.assert_called_with(kong_admin_url + 'apis/',
                                         headers={},
                                         data={'name': name,
                                               'hosts': host,
                                               'uris': None,
                                               'strip_uri': None,
                                               'preserve_host': None,
                                               'upstream_url': url})


def test_invalid_preserve_host(fake, kong, session_stub, kong_admin_url, invalid_value):
    # Setup
    name = fake.api_name()
    uri = fake.api_path()
    url = fake.url()

    # Exercise
    with pytest.raises(ValueError):
        kong.create(name=name, upstream_url=url, uris=uri, preserve_host=invalid_value)

    # Verify
    session_stub.post.assert_called_with(kong_admin_url + 'apis/',
                                         headers={},
                                         data={'name': name,
                                               'hosts': None,
                                               'uris': uri,
                                               'strip_uri': None,
                                               'preserve_host': invalid_value,
                                               'upstream_url': url})


def setup_test_update(fake):
    url = fake.url()
    name = fake.api_name()
    host = fake.domain_name()

    new_url = fake.url()
    new_host = fake.domain_name()
    new_path = fake.api_path()
    return url, name, host, new_url, new_host, new_path


def test_update_by_id(fake, kong, session_stub, kong_admin_url):
    # Setup
    url, name, host, new_url, new_host, new_path = setup_test_update(fake)

    # Exercise
    result = kong.create(upstream_url=url, name=name, hosts=host)

    kong.update(result['id'], upstream_url=new_url, uris=new_path, hosts=new_host)

    # Verify
    session_stub.patch.assert_called_with(kong_admin_url + 'apis/' + result['id'] + '/',
                                          headers={},
                                          data={'upstream_url': new_url,
                                                'uris': new_path,
                                                'hosts': new_host})


def test_update_by_name(fake, kong, session_stub, kong_admin_url):
    # Setup
    url, name, host, new_url, new_host, new_path = setup_test_update(fake)

    # Exercise
    kong.create(upstream_url=url, name=name, hosts=host)

    kong.update(name, upstream_url=new_url, uris=new_path, hosts=new_host)

    # Verify
    session_stub.patch.assert_called_with(kong_admin_url + 'apis/' + name + '/',
                                          headers={},
                                          data={'upstream_url': new_url,
                                                'uris': new_path,
                                                'hosts': new_host})


def test_list(fake, kong, session_stub, kong_admin_url):
    # Setup
    amount = 5

    host_list = [fake.domain_name() for _ in range(amount)]
    for host in host_list:
        kong.create(upstream_url=fake.url(), name=fake.api_name(), hosts=host)

    # Exercise
    api_list = kong.list()['data']

    # Verify
    query_params = {'size': 100}
    url = add_url_params(kong_admin_url + 'apis/', query_params)

    session_stub.get.assert_called_with(url,
                                        headers={})
    assert len(api_list) == len(host_list)


def setup_kong_with_apis(kong, fake):
    upstream_url_list = [fake.url() for _ in range(fake.random_int(2, 20))]
    for upstream_url in upstream_url_list:
        kong.create(upstream_url=upstream_url, name=fake.api_name(), hosts=fake.domain_name())
    return upstream_url_list


# pylint: disable=invalid-name
def test_list_filter_by_upstream_url(fake, kong, session_stub, kong_admin_url):
    # Setup
    upstream_url_list = setup_kong_with_apis(kong, fake)
    index = fake.random_int(0, len(upstream_url_list)-1)

    # Exercise
    kong.list(upstream_url=upstream_url_list[index])

    # Verify
    query_params = {'size': 100, 'upstream_url': upstream_url_list[index]}
    url = add_url_params(kong_admin_url + 'apis/', query_params)

    session_stub.get.assert_called_with(url, headers={})


def test_list_filter_with_size(fake, kong, session_stub, kong_admin_url):
    # Setup
    upstream_url_list = setup_kong_with_apis(kong, fake)
    size = fake.random_int(1, len(upstream_url_list)-1)

    # Exercise
    kong.list(size=size)

    # Verify
    query_params = {'size': size}
    url = add_url_params(kong_admin_url + 'apis/', query_params)

    session_stub.get.assert_called_with(url, headers={})


def test_delete_by_id(fake, kong, session_stub, kong_admin_url):
    # Setup
    url1 = fake.url()

    result1 = kong.create(upstream_url=url1, name=fake.api_name(), hosts=fake.domain_name())

    # Exercise
    kong.delete(result1['id'])

    # Verify
    url = kong_admin_url + 'apis/' + result1['id'] + '/'
    session_stub.delete.assert_called_with(url, headers={})


def test_delete_by_name(fake, kong, session_stub, kong_admin_url):
    # Setup
    url1 = fake.url()
    name = fake.api_name()

    kong.create(upstream_url=url1, name=name, hosts=fake.domain_name())

    # Exercise
    kong.delete(name)

    # Verify
    url = kong_admin_url + 'apis/' + name + '/'
    session_stub.delete.assert_called_with(url, headers={})
