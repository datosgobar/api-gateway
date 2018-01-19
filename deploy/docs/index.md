# API management - Deployment

Bienvenido a la documentación de "deployment" para API Management

## Consideraciones

### Primera conexión

Antes de usar el `playbook`, debemos agregar la clave pública de la máquina de deployment a todas las demas máquinas.
Ansible trabaja accediendo a cada una de ellas por SSH y la conexión SSH con contraseña debería estar desactivada.

Despues de agregar esas claves públicas, debemos conectarnos al menos una vez *desde la máquina de deployment*
para registrar las demás máquinas en el archivo `known_hosts`.

### Sudo y las contraseñas

Si para los servidores a los que se van a acceder se necesita una contraseña para poder usar `sudo`,
_todos los usuario que se usen tienen que tener la misma contraseña_.
Esto se debe a que ansible _solamente_ deja usar 1 contraseña para sudo en todos los servidores.

Por ejemplo, si se tienen dos servidores, web y elastic, no importa el nombre del usuario con que nos conectamos,
pero la contraseña debe ser la misma.

Si el usuario require _contraseña_ para usar comandos con `sudo`, previamente debemos correr el siguiente comando:
`export ANSIBLE_BECOME_ASK_PASS=true`. Esto hará que ansible nos pregunte *una sola vez* por esta contraseña.


### Punto de entrada

El script asume fuertemente que estamos accediendo a las máquinas desde _dentro de la misma red_.
O sea, todas las conecciones deben ser hechas a alguna IP del estilo "192.168.35.10".
Para que esto sea posible, se puede crear una máquina que sea solamente para correr el "deployment", _dentro de la misma red_.

### Conceptos

En el archivo `hosts.sample` puede verse la estructura básica de un inventario.
El mismo tiene un conjunto de servidores (A.K.A. host), grupos y supergrupos.

Un host (e.i. "kong0") representa *una máquina en la red*, la misma debe tener sus configuraciones únicas en un archivo `host_vars/<host>/vars.yml`.
Cabe destacar que, en este caso, "kong0" *no es un nombre que se resuelva a una IP*, es simplemente un alias a una IP.
En el archivo "vars.yml" podemos configurar como se conecta a este server (IP, puerto, usuario, etc.).


## Requerimientos

- OS: `Ubuntu 16.04`
- SSH client
- Python 3.x
- Python virtualenv
- Python pip

Para instalar estos requerimientos podemos correr:

```bash
sudo apt install openssh-client python3 python3-pip virtualenvwrapper -y
```
NOTA: Quizás sea necesario volver a entrar a la consola para que reconozca los comandos `mkvirtualenv` y `workon`

Luego creamos un nuevo "virtualenv" y lo activamos. Siempre que querramos correr el deploy, debemos usar activar el virtualenv.

```bash
mkvirtualenv -p $(which python3) deploy
workon deploy # Activa el virtualenv
```

Luego deberíamos, si ya no lo hicimos, clonar el presente repositorio e instalamos la version de
ansible especificada en para el repositorio con el comando `pip install -r requirements.txt`


## Inicializacion por ambiente

- testing (TBD)
- staging (TBD)
- production (TBD)

## Configuraciones de grupos y servidores

En estos documentos se encontrarán *más detalles* sobre como configurar más servidores o especificar configuraciones para los servidores.
Esta es documentación de referencia, no un *paso a paso* de como inicializar un ambiente.

- [Kong](groups/kong.md)


## Actualización

Para actualizar un ambiente, debe correrse el playbook de nuevo.
Esto actualizará el repositorio automaticamente.


## Vagrant & Tests

Se puede probar con [vagrant](http://www.vagrantup.com/) siguiendo los siguientes pasos:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
vagrant up --no-provision
# Incluyo el archivo de Vault como ejemplo
ansible-playbook -i inventories/vagrant/hosts --vault-password-file inventories/vagrant/vault_password.txt site.yml -v
```

Además con la variable de entorno "CHECKOUT_BRANCH" se puede configurar el branch que deseamos usar _dentro_ del servidor.

Para cambiar la cantidad de servidores de Elasticsearch debemos cambiar, dentro del archivo Vagranfile, la variable "ES_SERVER_COUNT" con un numero mayor a 1.
