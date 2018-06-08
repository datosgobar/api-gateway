from pytest import mark

from ..models import KongPluginCors


@mark.django_db()
def test_cors_plugin_is_disable_by_default(api_data):
    """
        al crear un cors plugin no se activa por default
    """
    # Setup
    api_data.enabled = True
    api_data.save()

    cors_plugin = KongPluginCors.objects.get(apidata=api_data)
    assert cors_plugin.enabled is False


@mark.django_db()
def test_cors_plugin_has_all_origins_by_default(api_data, kong_client):
    """
        Se activa cors cuando esta enable
    """
    # Setup
    api_data.enabled = True
    api_data.save()

    cors_plugin = KongPluginCors.objects.get(apidata=api_data)
    cors_plugin.enabled = True

    cors_plugin.manage_kong(kong_client)

    # Verify
    kong_client.plugins.create.assert_any_call(
        cors_plugin.plugin_name,
        api_name_or_id=api_data.kong_id,
        config={"origins": '*', }
    )


@mark.django_db()
def test_cors_plugin_allows_configure_origins(api_data, kong_client, cfaker):
    """
        Se activa cors cuando esta enable
    """
    # Setup
    api_data.enabled = True
    api_data.save()

    cors_plugin = KongPluginCors.objects.get(apidata=api_data)
    cors_plugin.enabled = True
    cors_plugin.origins = cfaker.uri()
    cors_plugin.manage_kong(kong_client)

    # Verify
    kong_client.plugins.create.assert_any_call(
        cors_plugin.plugin_name,
        api_name_or_id=api_data.kong_id,
        config={"origins": cors_plugin.origins, }
    )


@mark.django_db()
def test_when_cors_is_disabled_removes_from_api(api_data, kong_client, cfaker):
    """
        Se activa cors cuando esta enable
    """
    # Setup
    api_data.enabled = True
    api_data.save()

    cors_plugin = KongPluginCors.objects.get(apidata=api_data)
    cors_plugin.enabled = True
    cors_plugin.origins = cfaker.uri()
    cors_plugin.manage_kong(kong_client)
    cors_plugin.enabled = False
    plugin_id = cors_plugin.kong_id
    cors_plugin.manage_kong(kong_client)
    # Verify
    kong_client.plugins.delete.assert_any_call(plugin_id)
