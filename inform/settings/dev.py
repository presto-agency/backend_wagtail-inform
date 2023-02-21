import socket

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-+_@f-8v5nsz3gnwuh!m00&#x7m_yw913x@ob9wq)rpp!6!0s!)"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

GRAPPLE.update(
    {
        "EXPOSE_GRAPHIQL": True,
    }
)

BASE_URL = "http://localhost:8000"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
] + MIDDLEWARE

# Find IP of the Docker host
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
    "127.0.0.1",
    "10.0.0.2",
]


if os.getenv("ELASTIC_ENABLED") is not None:
    WAGTAILSEARCH_BACKENDS = dict(
        default=dict(
            BACKEND="wagtail.search.backends.elasticsearch7",
            INDEX="wagtail",
            TIMEOUT=5,
            URLS=[
                f"http://elastic:password@elastic:9200",
            ],
            OPTIONS={},
            INDEX_SETTINGS={},
        ),
    )

CORS_ALLOWED_ORIGINS = ["http://localhost"]

IMG_REPLACE_HOST = None

try:
    from .local import *
except ImportError:
    pass
