

# pylint: disable=invalid-name
def test_disabling_an_api_removes_it_from_the_kong_server(api_data,
                                                          kong_client,
                                                          api_manager,
                                                          faker):
    """
        al desactivar una api que tiene kong_id
        se elimina del server de kong
    """
    # Setup
    kong_id = faker.kong_id()
    api_data.enabled = False
    api_data.kong_id = kong_id

    # Exercise
    api_manager.manage(api_data, kong_client)

    # Verify
    kong_client.delete.assert_called_once_with(kong_id)


# pylint: disable=invalid-name
def test_enabling_an_api_creates_it_from_the_kong_server(api_data,
                                                         api_manager,
                                                         kong_client):
    """
        al activar una api que no tiene kong_id
        se crea en el server de kong
    """
    # Setup
    api_data.enabled = True

    # Exercise
    api_manager.manage(api_data, kong_client)

    # Verify
    kong_client.create.assert_called_with(api_data.upstream_url,
                                          name=api_data.name,
                                          strip_uri=api_data.strip_uri,
                                          hosts=api_data.hosts,
                                          uris=api_data.uris + '/(?=.)',
                                          preserve_host=api_data.preserve_host)


# pylint: disable=invalid-name
def test_creating_api_in_kong_server_sets_kong_id_in_api_data(api_data,
                                                              api_manager,
                                                              kong_client):
    """
        al crear una api en el server de kong
        se setea su kong_id en ApiData
    """
    # Setup
    api_data.enabled = True
    api_data.kong_id = None

    # Exercise
    api_manager.manage(api_data, kong_client)

    # Verify
    assert api_data.kong_id is not None


# pylint: disable=invalid-name
def test_updating_enabled_api_data_sends_an_update_to_kong_server(faker,
                                                                  api_data,
                                                                  api_manager,
                                                                  kong_client):
    """
        al cambiar la data de una api ya creada
        se manda un update de la api al server kong
    """
    # Setup
    api_data.enabled = True
    api_data.kong_id = None
    api_manager.manage(api_data, kong_client)

    # Exercise
    api_data.uris = faker.api_path()
    api_data.upstream_url = faker.url()

    api_manager.manage(api_data, kong_client)

    # Verify
    kong_client.update.assert_called_with(api_data.kong_id,
                                          upstream_url=api_data.upstream_url,
                                          name=api_data.name,
                                          strip_uri=str(api_data.strip_uri),
                                          hosts=api_data.hosts,
                                          uris=api_data.uris + '/(?=.)',
                                          preserve_host=str(api_data.preserve_host))


# pylint: disable=invalid-name
def test_updating_disabled_api_data_only_sends_update_to_doc_api(api_data,
                                                                 api_manager,
                                                                 kong_traffic_url,
                                                                 kong_client):
    """
        actualizar data de una api desactivada
        solo dispara comunicacion con el server kong
        para updatear la api de doc
    """
    # Setup
    api_data.enabled = False
    api_data.kong_id = None

    # Exercise
    api_manager.manage(api_data, kong_client)

    # Verify
    kong_client.create.assert_not_called()
    expected_upstream_url = ''.join([kong_traffic_url,
                                     'management/api/registry/docs/',
                                     api_data.name,
                                     '/'])
    kong_client.update.assert_called_once_with(api_data.name + '-doc',
                                               upstream_url=expected_upstream_url,
                                               uris=api_data.uris + '/$',
                                               hosts=api_data.hosts)
    kong_client.delete.assert_not_called()


def test_api_w_preserve_host(faker, api_data, api_manager, kong_client):
    # Setup
    preserve_host = faker.boolean()

    api_data.enabled = True
    api_data.preserve_host = preserve_host

    # Exercise
    api_manager.manage(api_data, kong_client)

    # Verify
    kong_client.create.assert_called_with(api_data.upstream_url,
                                          name=api_data.name,
                                          strip_uri=api_data.strip_uri,
                                          hosts=api_data.hosts,
                                          uris=api_data.uris + '/(?=.)',
                                          preserve_host=preserve_host)


def test_creating_an_api_also_creates_a_route_to_documentation(api_data,
                                                               api_manager,
                                                               kong_traffic_url,
                                                               kong_client):
    """
    Test: al crear una api en el modelo, tambien se crea una api en kong que
    direcciona hacia la documentacion.
    """
    # Setup
    api_data.id = None

    # Exercise
    api_manager.manage(api_data, kong_client)

    # Verify
    expected_upstream_url = ''.join([kong_traffic_url,
                                     'management/api/registry/docs/',
                                     api_data.name,
                                     '/'])
    kong_client.create.assert_called_once_with(expected_upstream_url,
                                               name=api_data.name + '-doc',
                                               uris=api_data.uris + '/$',
                                               hosts=api_data.hosts)


def test_deleting_and_api_deletes_its_route_to_documentation(api_data, api_manager, kong_client):
    # Exercise
    api_manager.delete_docs_api(api_data, kong_client)

    # Verify
    kong_client.delete.assert_called_once_with(api_data.name + '-doc')
