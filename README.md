# Kong API Gateway

Kong es un API Management que facilita la creación, publicación, mantenimiento, monitoreo y protección de API a cualquier escala.

## Índice 
* [Instalación](#instalación)
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
    
## Kong

- Levantar Kong

    `$ sudo kong start` 
    
- Test
    
    `$ export KONG_URL=http://localhost:8000`

    `$ http $KONG_URL`

    `import helpers`

- Registrar API o recurso

    `helpers.register_api('headers', 'https://httpbin.org/headers')`

    `$ http $KONG_URL/headers`
        
- Activar plugin [JWT](https://getkong.org/plugins/jwt/)

    `jwt = {'name': 'jwt', 'config.secret_is_base64': 'true'}`

    `helpers.configure_plugin('headers', jwt)`

    `$ http $KONG_URL/headers`
    
- Crear usuarios con credenciales para JWT

    `helpers.create_api_consumers('headers', [user1, user2])`  

- Listar usuarios o un usuario en particular para ver sus credenciales

    `$ http $KONG_URL/consumers/`

    `$ http $KONG_URL/consumers/<user>/jwt` (Devuelve **consumer_key** y **consumer_secret**.)

- Obtener token:
 
    `jwt_token = helpers.get_token_for(consumer_key, consumer_secret)`

- Consumir APIS

    `$ http $KONG_URL/headers 'Authorization:Bearer <jwt_token>'`
  
- Activar plugin [Rate limits](https://getkong.org/plugins/rate-limiting/)

    `rates = {'name': 'rate-limiting', 'config.minute': 10}`

    `helpers.configure_plugin('headers', rates)`


## Contacto
Te invitamos a [crearnos un issue](https://github.com/datosgobar/api-gateway/issues/new?title=Encontre-un-bug-en-api-gateway)
en caso de que encuentres algún bug o tengas comentarios de alguna parte de `api-gateway`. Para todo lo demás, podés mandarnos tu sugerencia o consulta a [datos@modernizacion.gob.ar](mailto:datos@modernizacion.gob.ar).
