from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

# DATABASE_URL='postgres://dbuser:dbpass@localhost/mydb'
DATABASES = {
    'default': env.db()
}

KONG_TRAFFIC_URL = env("KONG_TRAFFIC_URL", default="http://localhost:8000/")
KONG_ADMIN_URL = env("KONG_ADMIN_URL", default="http://localhost:8001/")
