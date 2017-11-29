# -*- coding: utf-8 -*-
from collections import defaultdict
from django.db import connections
from geo_admin.models import Consumer
import base64
import jwt
import os
import requests


KONG_URL = os.environ.get('KONG_URL', 'http://localhost:8000')


def configure_plugin(api, plugin_data):
    """Activa un plugin para una API."""
    try:
        plugins_url = KONG_URL + '/apis/%s/plugins' % api
        requests.post(plugins_url, data=plugin_data)
    except (requests.RequestException) as error:
        print(error)


def create_api_consumers(api, usernames):
    KONG_URL = os.environ.get('KONG_URL')
    try:
        consumers_url = KONG_URL + '/consumers'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        for name in usernames:
            response = requests.post(consumers_url, data={'username': name})
            if response.status_code == 201:
                print('Se creó el usuario "%s".' % name)
            credentials_url = KONG_URL + '/consumers/%s/jwt' % name
            response = requests.post(credentials_url, headers=headers, data={})
            if response.status_code == 201:
                print('Se crearon credenciales para el usuario "%s".' % name)
    except (requests.RequestException, ValueError) as error:
        print(error)


def get_token_for(consumer_key, consumer_secret):
    """Obtiene el token para las credenciales de un usuario."""
    if consumer is not None:
        return jwt.encode({'iss': consumer_key},
                          base64.b64decode(consumer_secret),
                          algorithm='HS256')
    return 'No se pudo obtener credenciales para el usuario ingresado.'


def register_api(api_name, uri):
    """Registra un recurso o API a la interfaz de KONG."""
    try:
        data = {
            'name': api_name,
            'uris': '/' + api_name,
            'upstream_url': uri
        }
        requests.post(KONG_URL + '/apis', data=data)
    except (requests.RequestException) as error:
        print(error)
