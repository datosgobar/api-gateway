import pytest

from ..exceptions import ConflictError


def test_create(fake, kong):
    # Setup
    url = fake.url()
    name = fake.api_name()
    host = fake.domain_name()

    # Exercise
    result = kong.create(upstream_url=url, name=name, hosts=host)

    # Verify
    assert kong.count() == 1
    assert result['upstream_url'] == url
    assert result['name'] == name
    assert host in result['hosts']
    assert result['id'] is not None
    assert result['created_at'] is not None
    assert 'uris' not in result


def test_create_conflict_name(fake, kong):
    # Setup
    url = fake.url()
    name = fake.api_name()
    host = fake.domain_name()

    # Exercise
    kong.create(upstream_url=url, name=name, hosts=host)
    assert kong.count() == 1

    with pytest.raises(ConflictError):
        kong.create(upstream_url=fake.url(), name=name, hosts=fake.domain_name())

    # Verify
    assert kong.count() == 1


def test_create_same_public_host(fake, kong):
    # Setup
    url = fake.url()
    name = fake.api_name()
    host = fake.domain_name()

    # Exercise
    kong.create(upstream_url=url, name=name, hosts=host)
    assert kong.count() == 1

    kong.create(upstream_url=fake.url(), name=fake.api_name(), hosts=host)

    # Verify
    assert kong.count() == 2


# pylint: disable=invalid-name
def test_create_missing_hosts_and_uris(fake, kong):
    # Setup
    result = None

    # Exercise
    with pytest.raises(ValueError):
        result = kong.create(name=fake.api_name(),
                             upstream_url=fake.url())

    # Verify
    assert result is None
    assert kong.count() == 0


def test_create_missing_hosts(fake, kong):
    # Exercise
    kong.create(name=fake.api_name(),
                upstream_url=fake.url(),
                uris=fake.api_path())

    # Verify
    assert kong.count() == 1


def test_create_missing_uris(fake, kong):
    # Exercise
    kong.create(name=fake.api_name(),
                upstream_url=fake.url(),
                hosts=fake.domain_name())

    # Verify
    assert kong.count() == 1


def test_update_by_id(fake, kong):
    # Setup
    url = fake.url()
    name = fake.api_name()
    dns = fake.domain_name()

    new_path = fake.api_path()
    new_url = fake.url()
    new_dns = fake.domain_name()

    # Exercise
    result = kong.create(upstream_url=url, name=name, hosts=dns)

    result3 = kong.update(result['id'], upstream_url=new_url, uris=new_path, hosts=new_dns)

    # Verify
    assert result3['id'] == result['id']
    assert result3['upstream_url'] == new_url
    assert new_path in result3['uris']
    assert len(result3['uris']) == 1
    assert new_dns in result3['hosts']
    assert len(result3['hosts']) == 1


def test_update_by_name(fake, kong):
    # Setup
    url = fake.url()
    name = fake.api_name()
    dns = fake.domain_name()

    new_path = fake.api_path()
    new_url = fake.url()
    new_dns = fake.domain_name()

    # Exercise
    result = kong.create(upstream_url=url, name=name, hosts=dns)

    result3 = kong.update(name, upstream_url=new_url, uris=new_path, hosts=new_dns)

    # Verify
    assert result3['id'] == result['id']
    assert result3['upstream_url'] == new_url
    assert new_path in result3['uris']
    assert len(result3['uris']) == 1
    assert new_dns in result3['hosts']
    assert len(result3['hosts']) == 1


def test_list(fake, kong):
    # Setup
    amount = 5

    host_list = [fake.domain_name() for _ in range(amount)]
    for host in host_list:
        kong.create(upstream_url=fake.url(), name=fake.api_name(), hosts=host)

    assert kong.count() == len(host_list)

    # Exercise
    api_list = kong.list()['data']

    # Verify
    api_hosts_list = []
    for api in api_list:
        for host in api['hosts']:
            api_hosts_list.append(host)

    assert len(api_list) == amount
    assert len(api_hosts_list) == amount
    for host in host_list:
        assert host in api_hosts_list


# pylint: disable=invalid-name
def test_list_filter_by_upstream_url(fake, kong):
    # Setup
    amount = 5

    upstream_url_list = [fake.url() for _ in range(amount)]
    for upstream_url in upstream_url_list:
        kong.create(upstream_url=upstream_url, name=fake.api_name(), hosts=fake.domain_name())

    assert kong.count() == len(upstream_url_list)

    # Exercise
    api_list = kong.list(upstream_url=upstream_url_list[4])['data']

    # Verify
    assert len(api_list) == 1


def test_list_filter_with_size(fake, kong):
    # Setup
    amount = 5

    upstream_url_list = [fake.url() for _ in range(amount)]
    for upstream_url in upstream_url_list:
        kong.create(upstream_url=upstream_url, name=fake.api_name(), hosts=fake.domain_name())

    assert kong.count() == len(upstream_url_list)

    # Exercise
    result = kong.list(size=3)
    assert result['next'] is not None
    assert len(result['data']) == 3


def test_delete_by_id(fake, kong):
    # Setup
    url1 = fake.url()

    result1 = kong.create(upstream_url=url1, name=fake.api_name(), hosts=fake.domain_name())

    # Exercise
    kong.delete(result1['id'])

    # Verify
    assert kong.list(id=result1['id'])['total'] == 0


def test_delete_by_name(fake, kong):
    # Setup
    url1 = fake.url()

    result1 = kong.create(upstream_url=url1, name=fake.api_name(), hosts=fake.domain_name())

    # Exercise
    kong.delete(result1['name'])

    # Verify
    assert kong.list(name=result1['name'])['total'] == 0
