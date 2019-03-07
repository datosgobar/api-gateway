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

MEDIA_URL = '/%s/media/' % URLS_PREFIX
STATIC_ROOT = (BASE_DIR - 1)('static')
STATIC_URL = '/%s/static/' % URLS_PREFIX

HTTPLOG2_ENDPOINT = env("HTTPLOG2_ENDPOINT", default="http://localhost:8000/management/api/analytics/queries/")

for queue in RQ_QUEUES.values():
    queue['ASYNC'] = False
