# API Management

## Setup

### Requerimientos

Este proyecto require python 3.6.
Python 3 puede ser instalado con [pyenv](https://github.com/pyenv/pyenv).

1. Usar [pyenv-installer](https://github.com/pyenv/pyenv-installer) para instalar pyenv
1. Ver las versiones de python disponibles: `pyenv install --list`
1. Instalar python 3. Ejemplo: `pyenv install 3.6.3` (3.6.3 o mayor)


Tambien [nodejs](https://nodejs.org/en/) es necesario para usar `eslint` y `jscpd`.

1. Instalar `nodejs`, esto se puede llevar a cabo mediante [nvm](https://github.com/creationix/nvm).
1. Instalar la version `7` de `nodejs`
1. Usar `npm` para instalar las dependencias: `npm install`


Opcionalmente se puede usar Docker y Docker Compose para desarrollo.

### Settings

Este proyecto adopta [The 12 factor methodology](https://12factor.net/).
Esto significa que todas las configuraciones deberian hacerse por variables de entorno. [(Factor III)](https://12factor.net/config).

## Configuracion Local

1. Crear un "virtualenv" con un nombre descriptivo: `pyenv virtualenv 3.6.3 my_virtualenv`
1. Crear un archivo `.python-version`: `echo "my_virtualenv" > .python-version`
1. Instalar los requerimientos: `pip install -r requirements/local.txt`
1. Instalar redis: `# apt-get install redis-server`

### Development with Docker

1. Build: `docker-compose build`
1. Iniciar los servicios: `docker-compose up -d`
1. Migrar la base de datos de kong: `docker-compose run kong kong migrations up`
1. Reiniciar kong: `docker-compose up -d kong`
1. Migrar la base de datos: `docker-compose run django /app/venv/bin/python manage.py migrate`
1. Crear un super usuario: `docker-compose run django /app/venv/bin/python manage.py createsuperuser`

### Activar el plugin de httplog2 en Docker

El plugin se agrega a la imagen de kong modificada, para permitir simular el comportamiento del kong de producción.

Para agregar este plugin a una API, primero debemos generar un token de acceso.

```
docker-compose run django /app/venv/bin/python manage.py drf_create_token admin
==> Generated token ea9fa26e47c78d8947cacb5ca5b2fa9c22e56718 for user admin
```

Finalmente debemos hacer la siguiente llamada a la API admin de Kong.
Debemos conocer previamente el ID de la API (A.K.A. kong_id).

```
API_ID=f9211efa-404f-4e4b-9024-91f58d1041e6
API_TOKEN=ea9fa26e47c78d8947cacb5ca5b2fa9c22e56718
curl localhost:8001/apis/$API_ID/plugins/ -d name=httplog2 -d config.endpoint=http://django:8080/api/analytics/queries/ -d config.token=$API_TOKEN
```

## Git hooks

* Instalar [git-hooks](https://github.com/git-hooks/git-hooks/).
* Instalar los hooks de git: `git hooks install`

## Tips:

## Server para desarrollo

* `./manage.py runserver`

## Consola de django

* `./manage.py shell`

* Con Docker: `docker-compose run django /app/venv/bin/python manage.py migrate`

## Tests

* `python manage.py test`

## Correr Lint/Style/CPD


* [Flake8](http://flake8.pycqa.org/en/latest/index.html): `scripts/flake8.sh`
* [Pylint](https://pylint.readthedocs.io/en/latest/): `scripts/pylint.sh`
* [Jscpd](https://github.com/kucherenko/jscpd): `scripts/jscpd.sh`
* [Eslint](https://eslint.org/): `scripts/eslint.sh`
