

# pylint: disable=invalid-name, unused-argument
def test_disabling_an_api_removes_it_from_the_kong_server(api_data,
                                                          kong_client,
                                                          cfaker,
                                                          db):
    """
        al desactivar una api que tiene kong_id
        se elimina del server de kong
    """
    # Setup
    kong_id = cfaker.kong_id()
    api_data.enabled = False
    api_data.kong_id = kong_id

    # Exercise
    api_data.manage_kong(kong_client)

    # Verify
    kong_client.apis.delete.assert_called_with(kong_id)


# pylint: disable=invalid-name
def test_enabling_an_api_creates_it_from_the_kong_server(api_data,
                                                         kong_client):
    """
        al activar una api que no tiene kong_id
        se crea en el server de kong
    """
    # Setup
    api_data.enabled = True

    # Exercise
    api_data.manage_kong(kong_client)

    # Verify
    kong_client.apis.create\
        .assert_any_call(name=api_data.name,
                         upstream_url=api_data.upstream_url,
                         strip_uri=api_data.strip_uri,
                         hosts=api_data.hosts,
                         uris=api_data.uri + '/(?=.)',
                         preserve_host=api_data.preserve_host)


# pylint: disable=invalid-name
def test_creating_api_in_kong_server_sets_kong_id_in_api_data(api_data, kong_client):
    """
        al crear una api en el server de kong
        se setea su kong_id en ApiData
    """
    # Setup
    api_data.enabled = True
    api_data.kong_id = None

    # Exercise
    api_data.manage_kong(kong_client)

    # Verify
    assert api_data.kong_id is not None


# pylint: disable=invalid-name
def test_updating_enabled_api_data_sends_an_update_to_kong_server(cfaker,
                                                                  api_data,
                                                                  kong_client):
    """
        al cambiar la data de una api ya creada
        se manda un update de la api al server kong
    """
    # Setup
    api_data.enabled = True
    api_data.kong_id = cfaker.uuid4()

    # Exercise
    api_data.uri = cfaker.api_path()
    api_data.upstream_url = cfaker.url()

    api_data.manage_kong(kong_client)

    # Verify
    kong_client.apis.update\
        .assert_any_call(api_data.kong_id,
                         upstream_url=api_data.upstream_url,
                         strip_uri=api_data.strip_uri,
                         hosts=api_data.hosts,
                         uris=api_data.uri + '/(?=.)',
                         preserve_host=api_data.preserve_host)


# pylint: disable=invalid-name
def test_updating_disabled_api_does_not_triggers_kong_communication(api_data,
                                                                    kong_client):
    """
        actualizar data de una api desactivada
        no dispara comunicacion con el server kong
    """
    # Setup
    api_data.enabled = False
    api_data.kong_id = None

    # Exercise
    api_data.manage_kong(kong_client)

    # Verify
    kong_client.apis.create.assert_not_called()
    kong_client.apis.update.assert_not_called()
    kong_client.apis.delete.assert_not_called()


def test_api_w_preserve_host(cfaker, api_data, kong_client):
    # Setup
    preserve_host = cfaker.boolean()

    api_data.enabled = True
    api_data.preserve_host = preserve_host

    # Exercise
    api_data.manage_kong(kong_client)

    # Verify
    kong_client.apis.create\
        .assert_any_call(name=api_data.name,
                         upstream_url=api_data.upstream_url,
                         strip_uri=api_data.strip_uri,
                         hosts=api_data.hosts,
                         uris=api_data.uri + '/(?=.)',
                         preserve_host=preserve_host)


def test_creating_an_api_also_creates_a_route_to_documentation(api_data,
                                                               kong_traffic_url,
                                                               kong_client):
    """
    Test: al crear una api en el modelo, tambien se crea una api en kong que
    direcciona hacia la documentacion.
    """
    # Setup
    api_data.enabled = True

    # Exercise
    api_data.manage_kong(kong_client)

    # Verify
    expected_upstream_url = ''.join([kong_traffic_url,
                                     'management/api/registry/docs/',
                                     api_data.name,
                                     '/'])

    kong_client.apis.create\
        .assert_any_call(name=api_data.name,
                         upstream_url=api_data.upstream_url,
                         uris=api_data.uri + '/(?=.)',
                         hosts=api_data.hosts,
                         preserve_host=api_data.preserve_host,
                         strip_uri=api_data.strip_uri)

    kong_client.apis.create\
        .assert_any_call(name=api_data.name + '-doc',
                         upstream_url=expected_upstream_url,
                         uris=api_data.uri + '/?$',
                         hosts=api_data.hosts)


def test_deleting_and_api_deletes_its_route_to_documentation(api_data, kong_client):
    # Exercise
    api_data._delete_docs_api(kong_client)

    # Verify
    kong_client.apis.delete\
        .assert_called_once_with(api_data.get_docs_kong_id())
