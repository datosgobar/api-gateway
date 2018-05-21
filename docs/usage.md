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

Es posible configurar un límite de llamadas ("rate limit") a la API por IP.
En el panel "Kong plugin rate limiting" podemos ver como hacerlo.
Luego de _tildar_ **enabled**, debemos configrar cuales son los limites de llamadas.
Los posibles valores configurables son:

- **second**: Llamadas por segundo
- **minutes**: Llamadas por minuto
- **hour**: Llamadas por hora
- **day**: Llamadas por día
