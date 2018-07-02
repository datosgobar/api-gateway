# Guía de uso

## Rate limiting

### A nivel API

Es posible configurar un límite de llamadas (a.k.a. "rate limit") a la API por IP.
En el panel "Kong plugin rate limiting" podemos ver como hacerlo,
en el panel "KONG API PLUGIN RATE LIMITINGS".
Luego de _tildar_ **enabled**, debemos configurar cuales son los limites de llamadas.
Los posibles valores configurables son:

- **second**: Llamadas por segundo
- **minutes**: Llamadas por minuto
- **hour**: Llamadas por hora
- **day**: Llamadas por día

### A nivel Consumer

Si estamos usando el plugin de autenticación por *JWT*, es posible establecer un
límite basado *en cada consumidor*. Este limite su puede configurar en al editar un
**Kong Consumer**. Además si la opción **Free tier** esta activada, es posible establecer
un limite único para todos los usuarios anónimos en conjunto.
Este limite se establece en el **kong consumer** que se crea automáticamente,
cuyo *applicant* es *anonymous*.

## Politicas

##### Siempre tiene prioridad el rate limiting mas especifico
Si se activa tanto rate limiting en la api con en su consumer solo se aplica
la cuota del consumer.

##### Rate limiting de una api es individual por cliente
De aplicarse rate limiting de una api a un cliente este tendrá su propia cuota,
 sin importar otras conexiones.

#### Todas las conexiones de un consumer comparten una cuota
Sin importar cuantas conexión se abran a una api, si estas se identifican
con un consumer en común entonces compartirán una quota de requests.

#### Consumers anónimos no tienen trato especial
Los consumers anónimos son consumers igual que cualquiera. Por lo cual
aplican las mismas políticas para ellos como para consumers no anónimos.

#### Conexiones anónimas comparten un mismo consumer anónimo
Al estar activa la opcion JWT, a cada conexión se asigna un consumer en base al token provisto.

- De proveer un token válido: se asigna el consumer correspondiente.
- De proveer un token invalido: se rechaza la conexión.
- De no proveer un token:
  - Si está activado **free tier**: se asigna el consumer anónimo correspondiente.
  - Si no está activado **free tier**: se rechaza la conexión.

Para mas informacion de autenticacion leer [JWT](jwt.md)