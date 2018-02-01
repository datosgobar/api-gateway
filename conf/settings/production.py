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

MEDIA_ROOT = env('MEDIA_ROOT')
STATIC_ROOT = env('STATIC_ROOT')
SECRET_KEY = env('DJANGO_SECRET_KEY')

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = [
    env("ALLOWED_HOST"),
    env("ALLOWED_HOST_IP"),
]

RAVEN_CONFIG = {
    'dsn': env('RAVEN_DSN', default=""),
}

INSTALLED_APPS += 'raven.contrib.django.raven_compat',

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default="")
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default="")
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default="")
EMAIL_USE_TLS = True
