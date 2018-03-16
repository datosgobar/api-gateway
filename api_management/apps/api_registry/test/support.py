from api_management.apps.api_registry.models import ApiData


def generate_api_data(name, upstream_url, uris, kong_id, api_id):
    api = ApiData(name=name,
                  upstream_url=upstream_url,
                  uris=uris,
                  kong_id=kong_id)
    api.id = api_id
    return api
