# Arquitectura de API Gateway

![Diagrama de alto nivel de la arquitectura de API Gateway](https://raw.githubusercontent.com/datosgobar/api-gateway/master/docs/arquitectura-api-gateway.png)

Los servicios de API Gateway están implementados como dos grandes componentes:

## Kong API Cluster

El punto de entrada a cualquier API publicada por API Gateway está implementado usando el producto de código abierto [Kong](https://konghq.com/), en su variedad _Community Edition_. Kong permite publicar APIs y montar los distintos servicios que se le brindan.

## Aplicación API Management

La aplicación API Management es una aplicación web que se utiliza para configurar la instancia de Kong. Basada en [Django 2.0](https://www.djangoproject.com) y [Python3](https://python.org) utiliza un cliente Python de Kong para configurar Kong luego de cada operación de configuración realizada por los administradores de la misma.

Esta aplicación permite configurar la instancia de Kong mediante una interfaz web, en vez de utilizar una sesión `bash` y un cliente `REST`.

Adicionalmente esta aplicación funciona como repositorio de las APIs configuradas en la aplicación, indicando los endpoints y los requerimientos de autenticación y rate-limiting.

![Diagrama de secuencia API Gateway](https://raw.githubusercontent.com/datosgobar/api-gateway/master/docs/secuencia-api-gateway.png)

El grueso de las funcionalidades de API Gateway se utilizan y configuran a través de API Management. El backoffice (admin de Django) se puede acceder en `/management/ingresar`. Ver - Documentación de uso [aquí](./usage.md)

