# API Gateway

**Versión**: 0.15.0

API Gateway es una aplicación para administrar, ordenar y facilitar la publicación de APIs de datos de la Administración Pública Nacional. Con API Gateway se puede:

* **Publicar APIs bajo un dominio común**: distintas ubicaciones (IPs o URIs) en la web bajo el mismo dominio. Permite administrar rutas y ambientes y dar de alta/baja APIs/ambientes con distintas rutas (/series, /georef), así como re-direccionar rápidamente.
    + Ej.: apis.datos.gob.ar
        - apis.datos.gob.ar/series
        - apis.datos.gob.ar/georef
* **Compilar documentación**: generar documentación de una API compatible con Open API o re-direccionar a la URI donde esta se aloje.
* **Administrar cuotas**: por IP o por usuario con token.
* **Autenticar usuarios**: con token propio.
* **Recolectar _analytics_**: envío a Google Analytics, generación de CSVs bajo autenticación y disponibilidad por API.

Esta documentación apunta a 3 públicos distintos:

* **Usuarios**: son los desarrolladores o administradores de alguna API, que desean darla de alta en API Gateway y usar sus servicios para administrarla.
* **Administradores**: son los administradores de API Gateway, y crean los usuarios para desarrolladores o administradores de alguna API que deseen usar la aplicación.
* **Desarrolladores**: son desarrolladores que quieren instalar y utilizar API Gateway en sus propios servidores.
