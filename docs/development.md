# API Management

## Setup

### Requerimientos

El sistema está pensado para correr bajo entornos *nix, en particular Ubuntu 16.04.

Este proyecto require python 3.6.
Python 3 puede ser instalado con [pyenv](https://github.com/pyenv/pyenv).

1. Usar [pyenv-installer](https://github.com/pyenv/pyenv-installer) para instalar pyenv
1. Ver las versiones de python disponibles: `pyenv install --list`
1. Instalar python 3. Ejemplo: `pyenv install 3.6.6` (3.6.6 o mayor)


Tambien [nodejs](https://nodejs.org/en/) es necesario para usar `eslint` y `jscpd`.

1. Instalar `nodejs`, esto se puede llevar a cabo mediante [nvm](https://github.com/creationix/nvm).
1. Instalar la version `7` de `nodejs`
1. Usar `npm` para instalar las dependencias: `npm install`


Las dependencias de la aplicación (Elasticsearch, Postgres, Redis, Kong) se manejan a través de Docker y docker-compose.

### Settings

Este proyecto adopta [The 12 factor methodology](https://12factor.net/).
Esto significa que todas las configuraciones deberian hacerse por variables de entorno. [(Factor III)](https://12factor.net/config).

### Paso previo 

Decidir un puerto bajo el cual correr la aplicación Django. Tanto Django como Kong usan como default el puerto 8000, por lo tanto Django debe correr bajo **otro** puerto arbitrario.

**La aplicación debe correr bajo la red interna obligatoriamente, para que el contenedor de Kong pueda llegar a la aplicación Django local**. Por ejemplo, se puede correr Django como`./manage.py runserver 192.168.1.181 7999`.
 
Para correr los próximos pasos, setear una variable `DJANGO_URL` con la URL (con schema) bajo la cual correrá la aplicación Django. Por ejemplo:

`DJANGO_URL=http://192.168.1.181:7999/`

La IP de la red interna se puede obtener a través de utilidades del sistema como `ip` o `ifconfig`, suele ser `192.168.*.*`.

### Setup de docker

1. Build: `docker-compose build`
1. Iniciar los servicios: `docker-compose up -d`
1. Migrar la base de datos de kong: `docker-compose run --rm kong kong migrations up`
1. Reiniciar kong: `docker-compose restart kong`
1. Agregar ruta de api management a kong `curl -X POST localhost:8001/apis -d name=management -d upstream_url=$DJANGO_URL -d uris=/management -d strip_uri=false`

### Configuracion Local

1. Crear un "virtualenv" con un nombre descriptivo: `pyenv virtualenv 3.6.6 my_virtualenv`
1. Crear un archivo `.python-version`: `echo "my_virtualenv" > .python-version`
1. Instalar los requerimientos: `pip install -r requirements/local.txt`
1. Copiar el archivo `conf/settings/.env.local` a `conf/settings/.env` (y reemplazar las variables de ser necesario)
1. Migrar la base de datos: `./manage.py migrate`
1. Crear un super usuario: `./manage.py createsuperuser`


### Correr la aplicación

Finalmente, se puede correr la aplicación con `./manage.py runserver <IP RED INTERNA> <PUERTO>`, y acceder a través de kong en `http://localhost:8000`.

### Workers

Por defecto la configuración local no utiliza workers asincrónicos, pero pueden ser activados seteando `queue['ASYNC'] = True` en el ciclo `for` dentro de `conf/settings/local.py`.

### Migraciones de la API de Kong
Casi todos los modelos de la aplicación `api_registry` requieren hacer una migración de las APIs de Kong (con actualizar una API es suficiente). A continuación se listan los encontrados hasta la fecha:

`KongObject`, `KongApi`, `KongApiPlugin`, `KongPlugin`, `KongConsumerManager`, `KongConsumer`, `JwtCredentialManager`, `JwtCredential`, `TokenRequest`, `KongPluginRateLimiting`, `KongApiPluginRateLimiting`, `KongApiPluginHttpLog`, `KongApiPluginJwt`, `KongApiPluginAcl`, `AclGroup`, `KongConsumerPlugin`, `KongConsumerPluginRateLimiting`, `KongApiPluginCors`, `RootKongApi`, 



### Git hooks

* Instalar [git-hooks](https://github.com/git-hooks/git-hooks/).
* Instalar los hooks de git: `git hooks install`

## Tips:

#### Server para desarrollo

* `./manage.py runserver`

#### Consola de django

* `./manage.py shell`

* Con Docker: `docker-compose run django python3 manage.py migrate`

#### Tests

* `python manage.py test`

#### Correr Lint/Style/CPD


* [Flake8](http://flake8.pycqa.org/en/latest/index.html): `scripts/flake8.sh`
* [Pylint](https://pylint.readthedocs.io/en/latest/): `scripts/pylint.sh`
* [Jscpd](https://github.com/kucherenko/jscpd): `scripts/jscpd.sh`
* [Eslint](https://eslint.org/): `scripts/eslint.sh`
