# -*- coding: utf-8 -*-
import base64
import jwt
import os
import requests


KONG_ADMIN = os.environ.get('KONG_ADMIN', 'http://localhost:8001')


def configure_plugin(api, plugin_data):
    """Activa un plugin para una API o recurso.

    Args:
        api (str): Nombre de la API o recurso donde activar el plugin.
        plugin_data (dict): Información de configuración del plugin.
    """
    try:
        plugins_url = KONG_ADMIN + '/apis/%s/plugins' % api
        requests.post(plugins_url, data=plugin_data)
    except (requests.RequestException) as error:
        print(error)


def create_api_consumers(usernames):
    """Crea usuarios consumidores de la API junto con sus credenciales JWT.

    Args:
        usernames (list): Nombres de usuarios a registrar.
    """
    if not isinstance(usernames, list):
        raise ValueError('El parámetro "usernames" debe ser una lista.')
    try:
        consumers_url = KONG_ADMIN + '/consumers'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        for name in usernames:
            response = requests.post(consumers_url, data={'username': name})
            if response.status_code == 201:
                print('Se creó el usuario "%s".' % name)
            credentials_url = KONG_ADMIN + '/consumers/%s/jwt' % name
            response = requests.post(credentials_url, headers=headers, data={})
            if response.status_code == 201:
                print('Se crearon credenciales para el usuario "%s".' % name)
    except (requests.RequestException, ValueError) as error:
        print(error)


def get_token_for(consumer_key, consumer_secret):
    """Obtiene el token para las credenciales de un usuario.

    Args:
        consumer_key (str): Clave asociada al usuario.
        consumer_secret (str): Secreto asociado al usuario.

    Returns:
        (str): Token de autenticación.
    """
    if consumer_key and consumer_secret:
        return jwt.encode({'iss': consumer_key},
                          base64.b64decode(consumer_secret),
                          algorithm='HS256')
    return 'No se pudo obtener credenciales para el usuario ingresado.'


def register_api(api_name, uri):
    """Registra un recurso o API a la interfaz de KONG.

    Args:
        api_name: Nombre de la API o recurso.
        uri: URI de la API o recurso.
    """
    try:
        data = {
            'name': api_name,
            'uris': '/' + api_name,
            'upstream_url': uri
        }
        requests.post(KONG_ADMIN + '/apis', data=data)
    except (requests.RequestException) as error:
        print(error)
