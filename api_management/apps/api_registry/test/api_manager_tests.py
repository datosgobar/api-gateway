from ..models import ApiManager


def test_disabling_an_api_deletes_it_in_kong_server(api_data, kong_client, faker):
    """
        al desactivar una api que tiene kong_id
        se elimina del server de kong
    """
    # Setup
    kong_id = faker.kong_id()
    api_data.enabled = False
    api_data.kong_id = kong_id

    # Exercise
    ApiManager.manage(api_data, kong_client)

    # Verify
    kong_client.delete.assert_called_once_with(kong_id)


def test_enabling_an_api_creates_it_in_kong_server(api_data, kong_client):
    """
        al activar una api que no tiene kong_id
        se crea en el server de kong
    """
    # Setup
    api_data.enabled = True

    # Exercise
    ApiManager.manage(api_data, kong_client)

    # Verify
    kong_client.create.assert_called_once_with(api_data.upstream_url,
                                               name=api_data.name,
                                               strip_uri=api_data.strip_uri,
                                               uris=api_data.uri)


def test_creating_api_in_kong_server_sets_kong_id_in_api_data(api_data, kong_client):
    """
        al crear una api en el server de kong
        se setea su kong_id en ApiData
    """
    # Setup
    api_data.enabled = True
    api_data.kong_id = None

    # Exercise
    ApiManager.manage(api_data, kong_client)

    # Verify
    assert api_data.kong_id is not None


def test_updating_enabled_api_data_sends_an_update_to_kong_server(faker, api_data, kong_client):
    """
        al cambiar la data de una api ya creada
        se manda un update de la api al server kong
    """
    # Setup
    api_data.enabled = True
    api_data.kong_id = None
    ApiManager.manage(api_data, kong_client)

    # Exercise
    api_data.uri = faker.api_path()
    api_data.upstream_url = faker.url()

    ApiManager.manage(api_data, kong_client)

    # Verify
    kong_client.update.assert_called_once_with(api_data.kong_id,
                                               upstream_url=api_data.upstream_url,
                                               name=api_data.name,
                                               strip_uri=str(api_data.strip_uri),
                                               uris=api_data.uri)


def test_updating_disabled_api_data_does_not_send_update_to_kong_server(faker, api_data, kong_client):
    """
        actualizar data de una api desactivada
        no dispara comunicacion con el server kong
    """
    # Setup
    api_data.enabled = False
    api_data.kong_id = None

    # Exercise
    ApiManager.manage(api_data, kong_client)

    # Verify
    kong_client.create.assert_not_called()
    kong_client.update.assert_not_called()
    kong_client.delete.assert_not_called()
