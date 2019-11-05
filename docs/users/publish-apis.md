# Publicar APIs bajo un dominio común

## Dar de alta una API

Luego de iniciar sesión como administradores, debemos ir a la página de creación de `KongApi`s.
Al acceder al formulario, sólo tres campos serán requeridos.

**name**: Nombre que le daremos a la API internamente. Será único en el sistema y no podrá cambiarse luego de ingresado.
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

### Modificaciones sobre la llamada

#### strip_uri

Es posible evitar que el la **URI** que definimos no llegue como parte de la llamada al **upstream url**.
Por ejemplo, pudiéramos querer definir una **URI** del estilo `/miapi1`, pero que al servidor solo le llegue lo que
este después de ese "path". Esto es posible lograrlo al _tildar_ el campo **strip uri** en el panel "advanced".

#### preserve_host

Se puede forzar que la api reciba en el header host, el valor recibido en api management.
Por default, se envía el host con el cual api management conoce a su api. Para mas informacion consultar
la [documentación de kong](https://docs.konghq.com/0.12.x/proxy/#the-preserve_host-property) al respecto.
