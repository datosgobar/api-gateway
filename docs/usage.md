# Guía de uso

## Alta de una API

Luego de iniciar sesión como administradores, debemos ir a la página de creación de `KongApi`s.
Al acceder al formularo, sólo tres compos serán requeridos.

**name**: Nombre que le daremos a la API internamente. Será unico en el sistema y no podrá cambiarse luego de ingresado.
Debe ser un valor alfanumérico y solo acepta estos `- _ ~` caracteres especiales.
Ejemplo: `series-tiempo-testing`

**upstream url**: Debe ser el upstream a donde se redireccionarán las llamadas. Debe incluir el protocolo.
Puede ser una dominio o una IP interna o externa.
Puede incluir el "path", pero no es lo más común.
Ejemplo: `http://192.168.65.4`.

**URI**: "Path" que servirá para verificar si una llamada debe ser redireccionada al "upstream url".
Debe empezar con `/` y no debe terminar con `/`.
Ejemplos: `/series`, `/georef`

**enabled**: Define si una API está activada o no.


## Configuraciones opcionales

### Documentación

#### Swagger

Por defecto, si configuramos la API con una `URI` del estilo `/series`, no se mostrará nada
en ese "path". Para mostrar la documentación de la API en ese "path" usando [swagger.io](http://swagger.io/), debemos
Llenar al campo **documentation url** con la URL al `yaml` con la definición de la API.
Esta URL _debe ser de público acceso_.

#### Redirección a la documentación

Es posible usar el mismo campo para lograr que el usuario sea redireccionado a una documentación fuera del control de
API gateway. Para ello debemos _destildar_ el campo **use swagger** (en el panel "advanced").
Esto hará que la aplicación devuelva un código HTTP 302, y redireccionará al usuario a la URL definida en **documentation url**.

### Modificaciones sobre la llamada

Es posible evitar que el la **URI** que definimos no llegue como parte de la llamada al **upstream url**.
Por ejemplo, pudieramos querer definir una **URI** del estilo `/miapi1`, pero que al servidor solo le llegue lo que
este después de ese "path". Esto es posible lograrlo al _tildar_ el campo **strip uri** en el panel "advanced".

## Logs

Es posible, con una penalidad en el rendimiento de la API, lograr guardar todas las llamadas que se hacen a la misma.
En el panel "kong plugin HTTP logs" podremos activar esta funcionalidad.
Primero debemos proveer una **api key** para que puedan guardarse los registros de las llamadas, y finalmente debemos
activar la funcionalidad al _tildar_ el campo **enabled**.

Las llamadas a la aplicación serán registradas bajo la sección "Analytics", en el modelo `Query`.

## Rate limiting

### A nivel API

Es posible configurar un límite de llamadas (a.k.a. "rate limit") a la API por IP.
En el panel "Kong plugin rate limiting" podemos ver como hacerlo,
en el panel "KONG API PLUGIN RATE LIMITINGS".
Luego de _tildar_ **enabled**, debemos configrar cuales son los limites de llamadas.
Los posibles valores configurables son:

- **second**: Llamadas por segundo
- **minutes**: Llamadas por minuto
- **hour**: Llamadas por hora
- **day**: Llamadas por día

### A nivel Consumer

Si estamos usando el plugin de autenticacion por *JWT*, es posible establecer un
límite basado *en cada consumidor*. Este limite su puede configurar en al editar un
**Kong Consumer**. Ademas si la opcion **Free tier** esta activada, es posible establecer
un limite unico para todos los usuarios anonimos en conjunto.
Este limite se establece en el **kong consumer** que se crea automaticamente,
cuyo *applicant* es *anonymous*.

## JWT

Es posible requerir la autenticacion para el uso de una aplicacion.
Mediante el panel "KONG API PLUGIN JWTS" podemos activar este mecanismo.
Al activar este plugin, la aplicacion intentara autenticar usuario *por API*, y se
los identificara como **kong consumers**.

Si la opcion **Free tier** esta activa, los usuarios sin token lograran acceder a la
API pero identificados como un *consumer anonimo* (a.k.a. "anonymous consumer").
En caso contrario a los usuario sin token no se les permitira el accedo a la API.

Para dar de alta un nuevo **kong consumer** es necesario crear un nuevo **Token requests**.
Una vez creado, debemos aceptarlo mediante seleccionarlo en la pagina de listado de "token requests"
y usando la accion *ACCEPT*.

Esto nos creara un nuevo **Kong Consumer**.

**NOTA:** Nunca cree un **kong consumer** directamente, solo mediante los **token request**.

En el nuevo **kong consumer** podemos ver una seccion "JWT CREDENTIALS".
La misma contiene el par *key*/*secret* para las llamada que el cliente necesita hacer.

Suponiendo que las claves son `bOgu3TainXFFOgLi2Q27EE7BRtXIBqdD` y `lR39z3kcMNAHc44NzOgj9CENWndMLYWQ` respectivamente,
podriamos usar el debugger de https://jwt.io/ o https://github.com/jpadilla/pyjwt para generar el token.

Al usar https://jwt.io nuestro payload debe lucir (haciendo uso de la "key"):

```
{
  "iss": "bOgu3TainXFFOgLi2Q27EE7BRtXIBqdD"
}
```

y en **VERIFY SIGNATURE** ponemos el "secret".

Al usar `pyjwt` podemos generarlo por linea de comando:

```
pyjwt --key=lR39z3kcMNAHc44NzOgj9CENWndMLYWQ encode iss=bOgu3TainXFFOgLi2Q27EE7BRtXIBqdD
# => eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJiT2d1M1RhaW5YRkZPZ0xpMlEyN0VFN0JSdFhJQnFkRCJ9.hxyvLkUYmrlonrFUoQ_Il1Y7RcJXYV5DERHBzR7paa0
```

Luego al usar nuestra aplicacion, debemos agregar el "header" **Authorization**:

```
url=http://localhost:8000/series/api/series/?ids=1.1_OGP_D_1993_A_17
token="$(pyjwt --key=lR39z3kcMNAHc44NzOgj9CENWndMLYWQ encode iss=bOgu3TainXFFOgLi2Q27EE7BRtXIBqdD)"

curl "$url" -H "Authorization: Bearer $token";
```



