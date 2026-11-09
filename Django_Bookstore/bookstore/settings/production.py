import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401, F403
from . import base
import dj_database_url

DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must contain at least 32 characters.")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("DJANGO_ALLOWED_HOSTS is required.")

INSTALLED_APPS = [app for app in base.INSTALLED_APPS if app != "debug_toolbar"]

MIDDLEWARE = [
    middleware
    for middleware in base.MIDDLEWARE
    if middleware != "debug_toolbar.middleware.DebugToolbarMiddleware"
]

SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = False

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Cloud PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ImproperlyConfigured("DATABASE_URL is required in production.")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# Cloud Redis
REDIS_URL = os.environ.get("REDIS_URL")

if not REDIS_URL:
    raise ImproperlyConfigured("REDIS_URL is required in production.")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "bookstore",
        "TIMEOUT": 300,
    }
}

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
