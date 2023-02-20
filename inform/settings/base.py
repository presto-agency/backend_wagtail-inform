
import os

from os import environ as env

VERSION = "2.0.122"

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)
SECRET_KEY = "django-insecure-+_@f-8v5nsz3gnwuh!m00&#x7m_yw913x@ob9wq)rpp!6!0s!0"

INSTALLED_APPS = [
    "home",
    "articles",
    "grapple",
    "graphene_django",
    "wagtail_transfer",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.modeladmin",
    "wagtail.contrib.settings",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail.core",
    "wagtail_feeds",
    "modelcluster",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "health_check",
    "health_check.db",
    "health_check.storage",
    "wagtail_color_panel",
    "wagtail_icon_picker",
    "wagtailorderable",
    "rest_framework",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware"
] + MIDDLEWARE

ROOT_URLCONF = "inform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]




# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, "static"),
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

# Embed configs

libsyn = {
    "endpoint": "https://oembed.libsyn.com",
    "urls": [
        "^https://oembed.libsyn.com.+$",
    ],
}

WAGTAILEMBEDS_FINDERS = [
    {
        "class": "wagtail.embeds.finders.oembed",
        "providers": [libsyn],
    },
    {
        "class": "wagtail.embeds.finders.oembed",
    },
]

# Wagtail settings

WAGTAIL_SITE_NAME = "Inform"
WAGTAIL_USAGE_COUNT_ENABLED = True

# Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = "http://example.com"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


GRAPHENE = {"SCHEMA": "grapple.schema.schema"}
GRAPPLE = {
    "APPS": ["home", "articles"],
    "ALLOWED_IMAGE_FILTERS": [
        "fill-1000x600",
        "fill-100x100",
        "fill-600x400",
        "fill-970x250",
        "max-100x100",
        "max-200x200",
        "max-876x876",
    ],
}

PRIVATE_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# OIDC roles which are to be granted unlimited access.
OIDC_SUPERUSER_ROLES = {"administrator"}
# OIDC roles which are to be granted access to the admin panel.
# Specific permissions need to be set up in Wagtail/Django groups editor
# by a superuser.
OIDC_STAFF_ROLES = {"administrator", "editor"}

# Only used in dev when running fetch_and_update_wp_images management command to add
# http://localhost:8000 to the URL it's replacing.
IMG_REPLACE_HOST = None

CORS_ALLOWED_ORIGINS = ["http://localhost"]

WAGTAILIMAGES_INDEX_PAGE_SIZE = 18
WAGTAIL_FILE_NAME_MAX_LENGTH = 255
ALLOWED_HOSTS = ['*']