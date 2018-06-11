from unittest.mock import patch

from pytest import mark

from ..models import KongPluginCors


@mark.django_db()
def test_disabled_by_default(api_data):
    """
        al crear un cors plugin no se activa por default
    """
    cors_plugin = KongPluginCors(apidata=api_data)
    assert cors_plugin.enabled is False


@mark.django_db()
def test_support_all_origins(api_data, kong_client):
    """
        Se activa cors cuando esta enable
    """
    # Setup
    api_data.enabled = True
    api_data.manage_kong(kong_client)
    cors_plugin = KongPluginCors(apidata=api_data)
    cors_plugin.enabled = True

    cors_plugin.manage_kong(kong_client)

    # Verify
    kong_client.plugins.create.assert_any_call(
        cors_plugin.plugin_name,
        api_name_or_id=api_data.kong_id,
        config={"origins": '*', }
    )


@mark.django_db()
def test_support_origins_conf(cors_plugin, kong_client):
    """
        Se activa cors cuando esta "enabled"
    """
    cors_plugin.manage_kong(kong_client)

    # Verify
    kong_client.plugins.create.assert_any_call(
        cors_plugin.plugin_name,
        api_name_or_id=str(cors_plugin.apidata.kong_id),
        config={"origins": cors_plugin.origins, }
    )


@mark.django_db()
def test_can_be_removed_from_api(cors_plugin, kong_client):
    """
        Se desactiva cors cuando esta no esta "enabled"
    """
    # Setup
    cors_plugin.manage_kong(kong_client)
    cors_plugin.enabled = False
    plugin_id = cors_plugin.kong_id
    cors_plugin.manage_kong(kong_client)
    # Verify
    kong_client.plugins.delete.assert_any_call(plugin_id)


@mark.django_db()
def test_enable_after_creating_api(cors_plugin, kong_client):
    api_data = cors_plugin.apidata
    api_data.enabled = False
    with patch("api_management.apps.api_registry.models.kong_client_using_settings",
               lambda: kong_client):
        api_data.save()
        cors_plugin.save()
        kong_client.plugins.create.assert_not_called()

    api_data.enabled = True
    with patch("api_management.apps.api_registry.models.kong_client_using_settings",
               lambda: kong_client):
        api_data.save()

    kong_client.plugins.create.assert_any_call(
        KongPluginCors.plugin_name,
        api_name_or_id=api_data.kong_id,
        config={"origins": cors_plugin.origins, }

    )
