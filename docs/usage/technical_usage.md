## Detalles técnicos de uso


#### Analytics

Los analytics de las apis con logs activados se obtienen haciendo GET `/management/api/analytics/queries/`.

Este endpoint requiere autenticacion por token.

Se puede obtener un token con `curl -X POST <kong>/management/api/token/ -d username=<username> -d password=<password>`

Para autenticarse enviar el token en el header `Authorization: Token <token>`.

Se pueden obtener queries con `curl -X GET <kong>/management/api/analytics/queries/ -H 'Authorization: Token <token>'
`


| Parametro   | Descripcion                                                     |
| -----------:|:--------------------------------------------------------------- |
| cursor      | Indica desplazamiento de pagina por cursor                      |
| kong_api_id | Id de api que se quiere filtrar.                                |


**Respuesta:**
```
HTTP 200 OK
```
```
{
    "next": "http://<kong>/management/api/analytics/queries/?cursor=xxxxxxx",
    "previous": null,
    "results": [
        {
            "id": 1,
            "ip_address": "123.123.123.123",
            "host": "datos.gob.ar",
            "uri": "/series/v1/series/",
            "api_data": 1,
            "querystring": "",
            "start_time": "2018-01-05T13:30:00-03:00",
            "request_time": "0.0001220000000000000000000",
            "status_code": 200,
            "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0"
        }
    ]
}
```

#### Generación de CSV de analytics

Todos los días, en el ambiente de deploy, se ejecuta el comando `python manage.py generate_analytics` para generar un archivo .csv el cual contiene la información de todas las Query que se hicieron el día anterior. Si se busca generar todos los analytics desde la primer Query realizada, hay que corre el comando `python manage.py generate_analytics --all`. Esto recorre todas las Query de la DB y genera un archivo .csv por día para cada una de ellas. Es un proceso asincrónico, por lo tanto, va a correr cuando los workers estén disponibles más allá de ver el mensaje en pantalla "Generando csv....". Este CSV puede accederse en el endpoint `/management/api/analytics/<kong_api_name>/analytics_<fecha>.csv`, por ejemplo: `/management/api/analytics/series/analytics_2018-06-30.csv`


#### Generación de CSV de indicadores por APIs

Todos los días, en el ambiente de deploy, se ejecuta el comando `python manage.py generate_indicators` para generar un archivo .csv el cual contiene la información de los indicadores por APIs. Cada row representa un día. Es un proceso asincrónico, por lo tanto, va a correr cuando los workers estén disponibles más allá de ver el mensaje en pantalla "Generando csv....". Este CSV puede accederse en el endpoint `/management/api/analytics/<kong_api_name>_indicadores.csv`, por ejemplo: `/management/api/analytics/series-tiempo-indicadores.csv`


#### Kong API: rate limiting

Hay 2 opciones para guardar los _rate limits_ de una API de Kong usados por el plugin KongPluginRateLimiting:
- cluster
- local

Cluster: guarda la información en la base de datos y nunca las borra. Es por ello que diseñamos un proceso que corre periódicamente para borrar los datos de _n_ días de antigüedad.

Local: guarda la información en la memoria RAM, lo cual tiene un tiempo de acceso más rápido y no nos tenemos que preocupar por el borrado.

**¿Cómo usar esta funcionalidad?**

Una KongAPI tiene un campo `policy` el cual permite elegir entre las opciones disponibles.

#### Borrado de analytics por día

Si por alguna razón se quieren borrar analytics, por ejemplo después de un test de stress, se puede utilizar el comando de django `delete_analytics`. Éste acepta una fecha y el nombre de una API, y borra todos los registros asociados a esos dos parámetros.

El nombre de la API es el `Name` con el que fue creado el modelo `KongApi` en el panel administrador.

La fecha debe estar en formato YYYY-MM-DD (ISO8601)

Ejemplo `./manage.py delete_analytics mi_api 2019-01-01`