from api_management.apps.api_registry.models import KongApi


def generate_api_data(name, upstream_url, uris, kong_id, api_id):
    api = KongApi(name=name,
                  upstream_url=upstream_url,
                  uri=uris,
                  kong_id=kong_id)
    api.id = api_id
    return api
