# Guía de uso

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
