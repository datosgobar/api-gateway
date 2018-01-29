from .base import *

DEBUG = True
TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']

# DATABASE_URL='postgres://dbuser:dbpass@localhost/mydb'
DATABASES = {
    'default': env.db()
}

INSTALLED_APPS += [
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
]
