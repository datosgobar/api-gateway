# Consumers

Para APIs protegidas bajo autenticación (es decir, con el plugin JWT activado), es necesario crear _consumidores_ de APIs. Estos consumers tendrán asociados un token [JWT](https://jwt.io/) que, a través de headers HTTP, podrán ser usados para autenticarse contra el backend. 

## Registrar un Consumer

Una opción para registrar consumidores es a través de [token requests](token_request.md), y luego aceptándose. 

Otra opción es crear consumidores directamente, instanciando nuevos modelos de Kong Consumers en el API Registry. 

Luego de cualquiera de estos dos pasos, el token JWT de la API asociado al usuario se encuentra bajo el modelo Kong Consumer creado por cualquiera de las dos acciones (en `/management/ingresar/api_registry/kongconsumer/`)

Un consumer está identificado por su dirección de correo electrónico y la API a la cual se asocia el JWT. No es posible crear tokens adicionales para esa combinación de usuario + API, ni usar el token generado para otras APIs. 
