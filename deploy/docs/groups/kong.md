# Agregar un servidor de Kong

Al agregar kong y configurarlo para que agregue las APIs automaticamente, se agregar el plugin de [rate-limiting](https://getkong.org/plugins/rate-limiting/)
con 5 llamadas por segundo y 10000 llamadas por hora.

En el ejemplo, se instalará kong en un servicor aparte.
Se pueden seguir los siguientes pasos:

Agregar un "host" al inventario, en este ejemplo, "kong0".  Agregar el archivo "inventories/staging/host_vars/kong0.yml", para
configurar cómo se accede a el mismo.

```
kong0

[kong]
kong0

[api_cluster:children]
kong

```

En el archivo "inventories/staging/group_vars/kong/vars.yml" agregar la configuración para configurar kong:

```yaml
---

kong_database_pass: "{{ kong_database_pass_vault }}"

```

En el archivo "inventories/staging/group_vars/kong/vault.yml" poner las variables sensibles:

```yaml
---

# reemplazar por el valor deseado
kong_database_pass_vault: "my_pass"

```


## Configuraciones


### Agregar APIs automaticamente

Para hacer que el playbook agregue APIs automaticamente, debemos agregar algunas variables.
Primero la variable `kong_add_map`, la cual es una lista de objectos `yaml`.

En el archivo "inventories/staging/group_vars/kong/vars.yml" agregar la configuración para configurar kong:

```yaml
---

# Otras variables ...

kong_api_map: "{{ kong_api_map_vault }}"

```

En el archivo "inventories/staging/group_vars/kong/vault.yml" poner las variables sensibles:

```yaml
---

# reemplazar por el valor deseado
kong_database_pass_vault: "my_pass"

# Debe ser una lista de objetos con las claves "name", "hosts", "upstream_url".
kong_api_map_vault:
  - {name: "stiempo-vagrant", hosts: "www.apis.datos.gob.ar", upstream_url: "http://192.168.35.10"}

```


### Configurar Rate-limit

El rate limit se configura por defecto.
Para configurar valores distintos para el rate-limit, se deben usar las siguientes variables:

```yaml

# Configura la cantidad de llamadas por segundo
kong_rate_limit_seconds: 5

# Configura la cantidad de llamadas por hora
kong_rate_limit_hour: 10000
```

Para desactivar el rate-limit, se puede usar la siguiente variable:

```yaml

# otras variables...
use_rate_limit: no

```


### Datadog

Para configurar Datadog, debemos primero obtener nuestra API key.

Luego agregamos la siguiente variable al grupo "kong":

```yaml
---

# Otras variables ...

kong_datadog_api_key: "{{ kong_datadog_api_key_vault }}"

```

En el archivo "inventories/staging/group_vars/kong/vault.yml" poner las variables sensibles:

```yaml
---

# reemplazar por la key correcta
kong_datadog_api_key_vault: "....":
```

### CORS

Para activar CORS en el sitio desde Kong, debemos agregar una variable mas, llamada `use_cors` con el valor `yes` a la configuracion de una API.

En el ejemplo anterior podria ser:

```

kong_api_map_vault:
  - {name: "stiempo-vagrant", hosts: "www.apis.datos.gob.ar", upstream_url: "http://192.168.35.10", use_cors: yes}

```
