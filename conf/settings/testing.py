from .base import *
import logging

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# we don't want logging while running tests.
logging.disable(logging.CRITICAL)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

DEBUG = False
TEMPLATE_DEBUG = False
TESTS_IN_PROGRESS = True

for queueConfig in RQ_QUEUES.values():
    queueConfig['ASYNC'] = False

KONG_ADMIN_URL = env("KONG_ADMIN_URL", default="http://localhost:8001/")
DOCS_URL = env("DOCS_URL", default="http://192.168.1.237:8080/api/registry/docs/")
