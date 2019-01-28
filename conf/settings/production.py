from .base import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG

environ.Env.read_env(SETTINGS_DIR('.env'))

ADMINS = (
    (env("ADMIN_NAME", default="Admin name"), env("ADMIN_EMAIL", default='admin_name@devartis.com')),
)

MANAGERS = ADMINS

# DATABASE_URL='postgres://dbuser:dbpass@localhost/mydb'
DATABASES = {
    'default': env.db()
}

STATIC_ROOT = env('STATIC_ROOT')
SECRET_KEY = env('DJANGO_SECRET_KEY')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = [host.strip() for host in env("ALLOWED_HOSTS").split(",")]

RAVEN_CONFIG = {
    'dsn': env('RAVEN_DSN', default=""),
}

INSTALLED_APPS += 'raven.contrib.django.raven_compat',

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default="")
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default="")
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default="")
EMAIL_USE_TLS = True

KONG_TRAFFIC_URL = env("KONG_TRAFFIC_URL")
KONG_ADMIN_URL = env("KONG_ADMIN_URL")


# Use default form base.py
URLS_PREFIX = env("URLS_PREFIX", default=URLS_PREFIX)

MEDIA_URL = '/%s/media/' % URLS_PREFIX
STATIC_URL = '/%s/static/' % URLS_PREFIX

for key in RQ_QUEUES:
    RQ_QUEUES[key]['HOST'] = env("REDIS_HOST")

HTTPLOG2_ENDPOINT = env("HTTPLOG2_ENDPOINT",
                        default="%s%s/api/analytics/queries/"
                                % (KONG_TRAFFIC_URL, URLS_PREFIX))
