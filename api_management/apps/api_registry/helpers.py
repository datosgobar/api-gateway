import kong.kong_clients as kong
from django.conf import settings


def coma_separated_list_of_regex(a_regex):
    return r'^\s*(' + a_regex + r')(,\s*(' + a_regex + r'))*\s*$'


def kong_client_using_settings():
    return kong.KongAdminClient(settings.KONG_ADMIN_URL)
