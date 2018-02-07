from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

# DATABASE_URL='postgres://dbuser:dbpass@localhost/mydb'
DATABASES = {
    'default': env.db()
}

KONG_ADMIN_URL = env("KONG_ADMIN_URL", default="http://localhost:8001/")
