# Guía de uso

## JWT

Es posible requerir la autenticación para el uso de una aplicación.
Mediante el panel "KONG API PLUGIN JWTS" podemos activar este mecanismo.
Al activar este plugin, la aplicación intentara autenticar usuario *por API*, y se
los identificara como **kong consumers**.

Si la opción **Free tier** esta activa, los usuarios sin token lograran acceder a la
API pero identificados como un *consumer anonimo* (a.k.a. "anonymous consumer").
En caso contrario a los usuario sin token no se les permitirá el accedo a la API.

Para dar de alta un nuevo **kong consumer** es necesario crear un nuevo **Token requests**.
Una vez creado, debemos aceptarlo mediante seleccionarlo en la pagina de listado de "token requests"
y usando la acción *ACCEPT*.

Esto nos creara un nuevo **Kong Consumer**.

En el nuevo **kong consumer** podemos ver una sección "JWT CREDENTIALS".
La misma contiene el par *key*/*secret* para las llamada que el cliente necesita hacer.

Suponiendo que las claves son `bOgu3TainXFFOgLi2Q27EE7BRtXIBqdD` y `lR39z3kcMNAHc44NzOgj9CENWndMLYWQ` respectivamente,
podríamos usar el debugger de https://jwt.io/ o https://github.com/jpadilla/pyjwt para generar el token.

Al usar https://jwt.io nuestro payload debe lucir (haciendo uso de la "key"):

```
{
  "iss": "bOgu3TainXFFOgLi2Q27EE7BRtXIBqdD"
}
```

y en **VERIFY SIGNATURE** ponemos el "secret".

Al usar `pyjwt` podemos generarlo por línea de comando:

```
pyjwt --key=lR39z3kcMNAHc44NzOgj9CENWndMLYWQ encode iss=bOgu3TainXFFOgLi2Q27EE7BRtXIBqdD
# => eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJiT2d1M1RhaW5YRkZPZ0xpMlEyN0VFN0JSdFhJQnFkRCJ9.hxyvLkUYmrlonrFUoQ_Il1Y7RcJXYV5DERHBzR7paa0
```

Luego al usar nuestra aplicación, debemos agregar el "header" **Authorization**:

```
url=http://localhost:8000/series/api/series/?ids=1.1_OGP_D_1993_A_17
token="$(pyjwt --key=lR39z3kcMNAHc44NzOgj9CENWndMLYWQ encode iss=bOgu3TainXFFOgLi2Q27EE7BRtXIBqdD)"

curl "$url" -H "Authorization: Bearer $token";
```



## Consumers

Para APIs protegidas bajo autenticación (es decir, con el plugin JWT activado), es necesario crear _consumidores_ de APIs. Estos consumers tendrán asociados un token [JWT](https://jwt.io/) que, a través de headers HTTP, podrán ser usados para autenticarse contra el backend. 

### Registrar un Consumer

Una opción para registrar consumidores es a través de [token requests](token_request.md), y luego aceptándose. 

Otra opción es crear consumidores directamente, instanciando nuevos modelos de Kong Consumers en el API Registry. 

Luego de cualquiera de estos dos pasos, el token JWT de la API asociado al usuario se encuentra bajo el modelo Kong Consumer creado por cualquiera de las dos acciones (en `/management/ingresar/api_registry/kongconsumer/`)

Un consumer está identificado por su dirección de correo electrónico y la API a la cual se asocia el JWT. No es posible crear tokens adicionales para esa combinación de usuario + API, ni usar el token generado para otras APIs. 


## Token Request

**api**: La api a la cual el consumer creado se subscribe.<br>
**applicant**: Nombre de solicitante, se usa para identificarlo.<br>
**contact email**: Email de contacto con el solicitante,
solo para uso administrativo.<br>
**consumer application**: Nombre de la aplicación que consume
la api en solicitud, sólo para uso administrativo.<br>
**requests per day**: Cantidad de requests estimados a la api por dia,
solo para uso administrativo.<br>
**state**: Estado del token request (`Aceptada` | `Rechazada` | `Pendiente`).<br>

### Cliente

Como cliente de la app, si quiero obtener un token para una api con
autenticación por [JWT](../apis/plugins/jwt.md), tengo que realizar una
peticion en la landing de dicha api, sea `/georef/` `/series/`

### Admin

Cómo admin puedo generar el token request desde el admin de api-mgmt.

## Aceptar o Rechazar Token Requests

Los tokens requests se aceptan o rechazan a traves
de acciones de django, en el admin.
