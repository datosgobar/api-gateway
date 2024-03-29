import logging
import os

from .base import *

MEDIA_ROOT = os.path.join((SETTINGS_DIR - 2).__str__(), 'media/test/')

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

KONG_TRAFFIC_URL = env("KONG_TRAFFIC_URL", default="http://localhost:8000/")
KONG_ADMIN_URL = env("KONG_ADMIN_URL", default="http://localhost:8001/")

HTTPLOG2_ENDPOINT = env("HTTPLOG2_ENDPOINT", default="%s%s/api/analytics/queries/"
                                                     % (KONG_TRAFFIC_URL, URLS_PREFIX))
DEFAULT_FROM_EMAIL = 'webmaster@localhost.com'
