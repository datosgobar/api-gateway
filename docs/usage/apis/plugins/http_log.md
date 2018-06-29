# Guía de uso

## Logs

Es posible, con una penalidad en el rendimiento de la API, lograr guardar todas las llamadas que se hacen a la misma.
En el panel "kong plugin HTTP logs" podremos activar esta funcionalidad.
Primero debemos proveer una **api key** para que puedan guardarse los registros de las llamadas, y finalmente debemos
activar la funcionalidad al _tildar_ el campo **enabled**.

Las llamadas a la aplicación serán registradas bajo la sección "Analytics", en el modelo `Query`.
