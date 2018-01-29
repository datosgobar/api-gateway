# Kong API Gateway

Kong es una herramienta para *API Management* que facilita la creación, publicación, mantenimiento, monitoreo y protección de APIs.

## Índice 
* [Instalación](#instalación)
* [Deployment](#deployment)
* [Contacto](#contacto)

## Instalación

[Documentación oficial](https://getkong.org/install/)


## Instalación en Ubuntu xenial

- Instalar dependencias

    `$ sudo apt-get update`
    
    `$ sudo apt-get install openssl libpcre3 procps perl httpie`

- Descargar e instalar paquete 

    `$ wget -O kong-community-edition-0.11.0.xenial.all.deb \
    https://bintray.com/kong/kong-community-edition-deb/download_file?file_path=dists/kong-community-edition-0.11.0.xenial.all.deb`
    
    `$ sudo dpkg -i kong-community-edition-0.11.0.xenial.all.deb`
    
- Generar archivo de configuración y modificar en caso de ser necesario

    `$ cp /etc/kong/kong.conf.default /etc/kong/kong.conf`

## Base de datos    

- Crear base de datos y usuario (PostgreSQL)

    ```postgresplsql
      CREATE USER kong; 
      CREATE DATABASE kong OWNER kong;
    ```

- Migraciones

    `$ sudo kong migrations up`
    
- Dependencias

    `pip install pyjwt`

## Kong

- Levantar Kong

    `$ sudo kong start` 
    
- Test
    
    `$ export KONG_ADMIN=http://localhost:8001` (Para configurar con helpers.py.)

    `$ export KONG_GATEWAY=http://localhost:8000` (Para consumir las APIs.)

    `$ http $KONG_GATEWAY` (Devuelve información del servicio.)

    `>>> import helpers`

- Registrar API o recurso

    `>>> helpers.register_api('headers', 'https://httpbin.org/headers')`

    `$ http $KONG_GATEWAY/headers`
    ```
    HTTP/1.1 200 OK
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Origin: *
    Connection: keep-alive
    Content-Length: 213
    Content-Type: application/json
    Date: Wed, 29 Nov 2017 18:26:04 GMT
    Server: meinheld/0.6.1
    Via: kong/0.11.0
    X-Kong-Proxy-Latency: 732
    X-Kong-Upstream-Latency: 655
    X-Powered-By: Flask
    X-Processed-Time: 0.00148606300354

    {
        "headers": {
            "Accept": "*/*", 
            "Accept-Encoding": "gzip, deflate", 
            "Connection": "close", 
            "Host": "httpbin.org", 
            "User-Agent": "HTTPie/0.9.2", 
            "X-Forwarded-Host": "localhost"
        }
    }
    ```
        
- Activar plugin [JWT](https://getkong.org/plugins/jwt/)

    `>>> jwt = {'name': 'jwt', 'config.secret_is_base64': 'true'}`

    `>>> helpers.configure_plugin('headers', jwt)`

    `$ http $KONG_GATEWAY/headers`
    ```
    HTTP/1.1 401 Unauthorized
    Connection: keep-alive
    Content-Type: application/json; charset=utf-8
    Date: Wed, 29 Nov 2017 18:27:54 GMT
    Server: kong/0.11.0
    Transfer-Encoding: chunked

    {
        "message": "Unauthorized"
    }
    ```
    
- Crear usuarios con credenciales para JWT

    `>>> helpers.create_api_consumers([user1, user2])`  

- Listar usuarios o un usuario en particular para ver sus credenciales

    `$ http $KONG_ADMIN/consumers/`

    `$ http $KONG_ADMIN/consumers/<user>/jwt` (Devuelve **consumer_key** y **consumer_secret**.)

- Obtener token:
 
    `>>> jwt_token = helpers.get_token_for(consumer_key, consumer_secret)`

- Consumir API

    `$ http $KONG_GATEWAY/headers 'Authorization:Bearer <jwt_token>'`
    ```
    HTTP/1.1 200 OK
    Access-Control-Allow-Credentials: true
    Access-Control-Allow-Origin: *
    Connection: keep-alive
    Content-Length: 483
    Content-Type: application/json
    Date: Wed, 29 Nov 2017 18:34:28 GMT
    Server: meinheld/0.6.1
    Via: kong/0.11.0
    X-Kong-Proxy-Latency: 188
    X-Kong-Upstream-Latency: 647
    X-Powered-By: Flask
    X-Processed-Time: 0.000800132751465

    {
        "headers": {
            "Accept": "*/*", 
            "Accept-Encoding": "gzip, deflate", 
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIU1NiJ9.eyJpc3MiOiJSVzBlNSZ2lSMzkzNGlacHFJTVFxaFZnYlNTb0NTbCJ9.KD93WD5IskBQrv9McgUyh8t9sUYI7poGlLLRe_UI", 
            "Connection": "close", 
            "Host": "httpbin.org", 
            "User-Agent": "HTTPie/0.9.2", 
            "X-Consumer-Id": "02870e1d-b215-4b74-8662-bf1efd0f6726", 
            "X-Consumer-Username": "user1", 
            "X-Forwarded-Host": "localhost"
        }
    }
    ```
  
- Activar plugin [Rate limits](https://getkong.org/plugins/rate-limiting/)

    `>>> rates = {'name': 'rate-limiting', 'config.minute': 10}`

    `>>> helpers.configure_plugin('headers', rates)`


## Deployment

Ver la [documentación](deploy/docs/index.md)

## Django App
Documentacion de desarrollo [aqui](docs/django.md)

## Contacto
Te invitamos a [crearnos un issue](https://github.com/datosgobar/api-gateway/issues/new?title=Encontre-un-bug-en-api-gateway)
en caso de que encuentres algún bug o tengas comentarios de alguna parte de `api-gateway`. Para todo lo demás, podés mandarnos tu sugerencia o consulta a [datos@modernizacion.gob.ar](mailto:datos@modernizacion.gob.ar).
