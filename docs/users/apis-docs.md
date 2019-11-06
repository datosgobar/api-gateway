# Compilar documentación

## Swagger

Por defecto, si configuramos la API con una `URI` del estilo `/series`, no se mostrará nada
en ese "path". Para mostrar la documentación de la API en ese "path" usando [swagger.io](http://swagger.io/), debemos
Llenar al campo **documentation url** con la URL al `yaml` con la definición de la API.
Esta URL _debe ser de público acceso_.

## Redirección a la documentación

Es posible usar el mismo campo para lograr que el usuario sea redireccionado a una documentación fuera del control de
API gateway. Para ello debemos _destildar_ el campo **use swagger** (en el panel "advanced").
Esto hará que la aplicación devuelva un código HTTP 302, y redireccionará al usuario a la URL definida en **documentation url**.
