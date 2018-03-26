# Testing

_Ultima actualizacion: 19/03/2018_

## Pre-requisitos

Antes de correr `ansible-playbook` para usar el deploy, es necesario tener los servidores configurados.

En esta documentacion se asume la presencia de los siguiente servidores:
- "deploy": Contendra el codigo y el acceso para correr `ansible-playbook`
- "kong": Contendra el servicio de Kong
- "web": Contendra los servidores `gunicorn` y `nginx`, asi como los workers de RQ.
- "db-cache": Contendra la base de datos `postgresql` y el servidor `redis`.

Los pre-requisitos son:

### Configuracion general

Los servidores deben cumplir con los siguientes puntos:

Nota: para el servidor de "deploy", el usuario no es necesario que sea "sudoer"

- Conocer los usuarios con los que nos conectaremos.
- Conocer las contraseñas de los usuarios.
- Que los usuarios sean "sudoers".
- Servidor SSH levantado.
- Servidor SSH configurado para no aceptar conexiones con contraseña.
- Todos en la misma _red privada_.

### Acceso desde maquina de deployment

La maquina de "deploy" debe poder acceder al resto de las maquinas mediante `ssh` sin necesidad de introducir una contraseña.
Para esto generamos, en la maquina de "deploy" y con el usuario de deployment, generamos un par de clave publica/privada con el siguiente comando:

Nota: No escribir ninguna "secure passphrase" ya que no seremos capaces de escribirla cuando se requiera.

```
ssh-keygen -t rsa -b 4096 -C "deploy-dev@apimgt-deploy-deploy01"
```

Luego agregamos la clave publica (`~/.ssh/id_rsa.pub`) al archivo `authorized_keys` de los otros servidores.

### Obtener codigo de la aplicacion

Para lograr obtener el codigo de la aplicacion, que sera clonando el repositorio de Github,
debemos agregar la clave publica del servidor a las "Deploy Keys" del repositorio.

Luego, en el servidor "deploy" y con el usuario de deployment, creamos el directorio "dev" y clonamos el repositorio:

```
mkdir ~/dev && cd ~/dev
git clone git@github.com:datosgobar/api-gateway.git
cd ~/dev/api-gateway/deploy
```

### Configuracion & setup inicial

Para este paso necesitamos tener instalado Python3 y Python3-virtualenv.
En Ubuntu 16.04:

```
sudo apt update
sudo apt install python3 python3-virtualenv
```

Luego, es necesario instalar los requerimientos en un virtualenv.
Para crear el virtualenv corremos:

```
cd ~/dev
virtualenv ./venv
```

Luego activamos el "virtualev" e instalamos los requerimientos para el deployment.

```
cd ~/dev/
. ./venv/bin/activate
cd api-gateway/deploy/
pip install -r requirements.txt
```

Despues de esto, deberiamos tener el binario `ansible` disponible.

## Configurar el inventario de ansible

Antes de correr el deployment, debemos configurar los servidores.
Si miramos el archivo `inventories/hosts.sample` veremos la version mas actualizada de la arquitectura.


```
kong0
psql-redis0
web0
rqworker0

[web]
web0

[rqworkers]
rqworker0

[django_application:children]
web
rqworkers

[postgresql]
psql-redis0

[redis]
psql-redis0

[kong]
kong0

[api_cluster:children]
kong
web
redis
rqworkers
postgresql
```


Este archivo debemos copiarlo y pegarlo en la subcarpeta que queremos, en el caso del ambiente de testing, seria:

```
ENVIRONMENT="testing"
cd ~/dev/api-gateway/deploy
mkdir "inventories/$ENVIRONMENT"
cp inventories/hosts.sample "inventories/$ENVIRONMENT/hosts"

```


### Configuracion especifica de cada host

En esta documentacion, asumiremos que tenemos los siguientes servidores e IPs:

web0: 192.168.65.1
rqworker0: 192.168.65.2
psql-redis0: 192.168.65.3
kong0: 192.168.65.4


Luego debemos configurar cada uno de los "hosts" definidos en ese archivo.

Para eso crearemos los directorios `group_vars/` y `host_vars/` _por fuera_ del directorio de la aplicacion:

```
mkir ~/dev/config/
cd ~/dev/config/
mkdir group_vars/ host_vars/

```

Luego agregaramos la configuracion para cada server con los siguientes archivos.

**host_vars/web0/vars.yml**

En este archivo podremos poner configuracion especifica del servidor "web".
Como se puede ver, sera el host a conectar, el puerto y con que usuario.

```yaml
---

ansible_host: "{{ vault_ansible_host }}"
ansible_port: "{{ vault_ansible_port }}"
ansible_user: "{{ vault_ansible_user }}"

```


**host_vars/web0/vault.yml**

En este archivo pondremos valores que podremos referencias, pero que terminaran siendo encriptados.
En el paso final se muestra como.

```yaml
---

# La ip real a donde conectarse desde el servidor de "deploy"
vault_ansible_host: 192.168.1.1
vault_ansible_port: 22
# El usuario real con el cual conectarse
vault_ansible_user: mi_usuario
# La contraseña con la cual poder correr comandos con "sudo"
ansible_become_pass: secure_pass
```

**host_vars/rqworker0/vars.yml**

En este archivo podremos poner configuracion especifica del servidor "worker0".

```yaml
---

ansible_host: "{{ vault_ansible_host }}"
ansible_port: "{{ vault_ansible_port }}"
ansible_user: "{{ vault_ansible_user }}"

```


**host_vars/rqworker0/vault.yml**

```yaml
---

# La ip real a donde conectarse desde el servidor de "deploy"
vault_ansible_host: 192.168.1.2
vault_ansible_port: 22
# El usuario real con el cual conectarse
vault_ansible_user: mi_usuario
# La contraseña con la cual poder correr comandos con "sudo"
ansible_become_pass: secure_pass
```

**host_vars/psql-redis0/vars.yml**

```yaml
---

ansible_host: "{{ vault_ansible_host }}"
ansible_port: "{{ vault_ansible_port }}"
ansible_user: "{{ vault_ansible_user }}"

# IP o Interfaz por la que postgresql escuchara conexiones
# "ansible_host" representa la IP previamente definida.
# Podria ser tambien "vault_ansible_host"
postgresql_listen_address: "{{ ansible_host }}"
```

**host_vars/psql-redis0/vault.yml**

```yaml
---

# La ip real a donde conectarse desde el servidor de "deploy"
vault_ansible_host: 192.168.1.3
vault_ansible_port: 22
# El usuario real con el cual conectarse
vault_ansible_user: mi_usuario_para_este_server
# La contraseña con la cual poder correr comandos con "sudo"
ansible_become_pass: secure_pass_para_este_server
```

**host_vars/kong0/vars.yml**

```yaml
---

ansible_host: "{{ vault_ansible_host }}"
ansible_port: "{{ vault_ansible_port }}"
ansible_user: "{{ vault_ansible_user }}"
```

**host_vars/kong0/vault.yml**

```yaml
---

# La ip real a donde conectarse desde el servidor de "deploy"
vault_ansible_host: 192.168.1.4
vault_ansible_port: 22
# El usuario real con el cual conectarse
vault_ansible_user: mi_usuario_para_este_otro_server
# La contraseña con la cual poder correr comandos con "sudo"
ansible_become_pass: secure_pass_para_este_otro_server
```

### Configuracion de grupos

Ademas de la configuracion para cada "host", debemos agregar la configuracion para los grupos, que
engloban conjunto de servidores. Por ejemplo, el grupo "web" engloba los servidores que tiene el servidor nginx y gunicorn,
el grupo "psql" los servidores con Postgrsql, etc.

**group_vars/postgresql/vars.yml**

```yaml
---

# Credenciales para la aplicacion web
postgresql_user: "{{ vault_postgresql_user }}"
postgresql_database_name: "{{ vault_postgresql_database_name }}"
postgresql_password: "{{ vault_postgresql_password }}"

# Credenciales para kong
kong_database_name: "{{ vault_kong_database_name }}"
kong_user: "{{ vault_kong_user }}"
kong_database_pass: "{{ vault_kong_database_pass }}"
```

**group_vars/postgresql/vault.yml**

```yaml
---

vault_postgresql_user: "mi_db_user"
vault_postgresql_database_name: "mi_db_name"
vault_postgresql_password: "mi_db_pass"

# Momentanemente es requerido que el usuario y la base de datos sean "kong"
vault_kong_database_name: "kong"
vault_kong_user: "kong"
vault_kong_database_pass: mi_kong_db_pass

```

**group_vars/web/vars.yml**


```yaml
---

django_urls_prefix: management

```


**group_vars/django_application/vars.yml**

```yaml
---

# Repositorio de donde clonar la aplicacion
application_clone_url: git@github.com:datosgobar/api-gateway.git
# Asume que no proveeremos la clave ssh para clonar la app.
application_deploy_ssh_key_required: no

# Configuracion de acceso a la base de datos
database_url: "{{ vault_database_url }}"

# Branch o tag de la aplicacion que se desea
checkout_branch: master


allowed_host: apis-dev.apis.datos.gob.ar
allowed_host_ip: 192.168.65.4

# URL de la aplicacion de kong
kong_traffic_url: "{{ vault_kong_traffic_url }}"
# URL de la aplicacion admin de kong
kong_admin_url: "{{ vault_kong_admin_url }}"

# Host o IP del servidor de redis
django_redis_host: "{{ vault_django_redis_host }}"

# Configuración para el manejo del plugin de log
kong_http_log2_endpoint: http://192.168.35.4:80/management/api/analytics/queries/
django_urls_prefix: management

# Configuración de google analytics para log
# [tid](https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#tid)
ga_tracking_id: UA-XXXX-Y

```

**group_vars/django_application/vault.yml**

```yaml
---

vault_database_url: psql://mi_db_user:mi_db_pass@192.168.65.2:5432/mi_db_name

vault_kong_traffic_url: http://192.168.35.4:80
vault_kong_admin_url: http://192.168.35.4:8001

vault_django_redis_host: 192.168.35.3

```


**group_vars/kong/vars.yml**

```yaml
---

# IP o interfaz por la que escuchara el admin de Kong
kong_admin_interface: "{{ ansible_host }}"

# Credenciales de la base de datos para kong
kong_database_pass: "{{ vault_kong_database_pass }}"
kong_database_host: "{{ vault_kong_database_host }}"

# Desactivamos por default el rate limit
use_rate_limit: false

# Esta lista de objectos permite definit APIs en kong sin tener que pasar por la aplicacion
#  web. En este caso configuramos la aplcacion web para que este en /management.
#  Los parametros aqui expuestos son los documentados por la API de KONG.
kong_api_map:
  - {
    name: "management",
    upstream_url: "{{ vault_api_management_upstream_url }}",
    uris: "/management",
    strip_uri: false
    }

```


**group_vars/kong/vault.yml**

```yaml
---

vault_kong_database_pass: mi_kong_db_pass
vault_kong_database_host: 192.168.65.3

vault_api_management_upstream_url: http://192.168.65.1
```


### Encriptacion de los archivos

Hasta ahora hemos escrito as credenciales en archivos de texto plano.
Para aumentar la seguridad los encriptaremos. Para eso debemos generar una clave propia que usaremos
en conjunto con `ansible-vault`.

Luego de que hemos generado la clave, corremos el comando:

```bash
cd ~/dev/config

ansible-vault encrypt host_vars/web0/vault.yml \
                host_vars/plsq-redis0/vault.yml \
                host_vars/kong0/vault.yml \
                group_vars/kong/vault.yml \
                group_vars/web/vault.yml \
                group_vars/postgresql/vault.yml
```

Este comando nos pedira una clave, la cual sera la que acabamos de generar.


### Crear los links de los archivos

Finalmente creamos los links:

```bash

cd ~/dev/config

ln -s $PWD/group_vars ~/dev/api-gateway/deploy/inventories/testing/group_vars
ln -s $PWD/host_vars ~/dev/api-gateway/deploy/inventories/testing/host_vars
```


## Pasos finales

Antes de correr el deployment completo, debemos configurar el servidor "web" para
que pueda clonar el proyecto. Esto se hara con un usuario "devartis" (default) que
no existe si aun no hemos corrido el deployment. Entonces, corramos parte del "playbook"
que nos crea este usuario:

```bash
. ~/dev/venv/bin/activate
cd ~/dev/api-gateway/deploy

ansible-playbook api_cluster.yml -i inventories/testing/hosts --ask-vault-pass
```

Este comando correra algunas tareas de configuracion y creara los usuarios en todos los servidores.
Tambien nos servira de prueba para ver si ansible puede conectarse y correr comandos en todos los servidores.
Antes de empezar a correr cualquier comando, `ansible-playbook` nos pedira la clave que usamos para encriptar
los archivos con `ansible-vault`.
Si todo va bien, deberiamos ver algo como (los valores de "changed" y "ok" pueden variar):

```
PLAY RECAP ***********************************************************************************************************************************************************************************
kong0                      : ok=18   changed=2    unreachable=0    failed=0
psql-redis0                : ok=18   changed=2    unreachable=0    failed=0
web0                       : ok=18   changed=2    unreachable=0    failed=0
```


Una vez asegurado, entramos al servidor que definimos como "web1" y nos logueamos como el usuario "devartis".
Correr estos comandos desde el serveridor de deploy:

```
@deploy-server$ ssh mi_user@192.168.65.1

# Una vez logueados, cambiamos de usuario
mi_user@web-server$ sudo su - devartis

devartis@web-server$ cat .ssh/id_rsa.pub
```

La clave publica que veremos debe ser copiada a las "deploy keys" del repositorio en Github.


## Deployment

Una vez configurada la key, podemos volver al servidor de deployment y correr todo el "playbook":

```

ansible-playbook site.yml -i inventories/testing/hosts --ask-vault-pass
```

Si es la primera vez que corremos este comando, puede llegar a tardar bastante, ya que tendra que instalar y configurar la aplicacion
por primera vez.

