import os
from urllib.parse import parse_qs, unquote, urlparse

from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load = load_dotenv(os.path.join(BASE_DIR, ".env"))

# Variable environment local or production
ENV = os.environ.get("ENV", "development")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")
if ENV == "production" and not SECRET_KEY:
    raise ImproperlyConfigured("SECRET_KEY must be set in production.")
SECRET_KEY = SECRET_KEY or "sfghdtjrfypjouis5414enrgizn51454gpozeuzenpfoiqerzn"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENV != "production"

ADMIN_URL = os.environ.get("ADMIN_URL", "admin/")

ALLOWED_HOSTS = [host for host in os.environ.get("ALLOWED_HOSTS", "127.0.0.1 localhost").split() if host]
render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if render_hostname and render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)
CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS", "http://127.0.0.1 http://localhost"
    ).split() if origin
]
if ENV == "production" and render_hostname:
    api_origin = f"https://{render_hostname}"
    if api_origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(api_origin)


# Application definition
DJANGO_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_extensions",
    "drf_yasg",
    "cloudinary",
    "cloudinary_storage",
    "channels",
]

LOCAL_APPS = [
    "apps.home",
    "apps.authentication",
    "apps.profiles",
    "apps.post",
    "apps.comment",
    "apps.follow",
    "apps.notification",
    "apps.bookmark",
    "apps.chat",
]

DEVELOP_APPS = []

if ENV != "production":
    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS + DEVELOP_APPS
else:
    INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # whitenoise
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # django cors headers middleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

MIDDLEWARE = MIDDLEWARE + [] if ENV != "production" else MIDDLEWARE


ROOT_URLCONF = "config.urls"


TEMPLATES_DIRS = [
    os.path.join(BASE_DIR, "templates"),
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": TEMPLATES_DIRS,
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


WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# Database
TYPE_DATABASE = os.environ.get("TYPE_DATABASE", "sqlite3")
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

if DATABASE_URL:
    parsed_database_url = urlparse(DATABASE_URL)
    if parsed_database_url.scheme not in {"postgres", "postgresql"}:
        raise ImproperlyConfigured("DATABASE_URL must use the postgres:// or postgresql:// scheme.")
    database_options = {}
    sslmode = parse_qs(parsed_database_url.query).get("sslmode", [None])[0]
    if sslmode:
        database_options["sslmode"] = sslmode
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(parsed_database_url.path.lstrip("/")),
            "USER": unquote(parsed_database_url.username or ""),
            "PASSWORD": unquote(parsed_database_url.password or ""),
            "HOST": parsed_database_url.hostname or "",
            "PORT": parsed_database_url.port or 5432,
            "OPTIONS": database_options,
            "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "600")),
            "CONN_HEALTH_CHECKS": True,
        }
    }
elif TYPE_DATABASE == "sqlite3":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("DB_ENGINE"),
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "HOST": os.environ.get("DB_HOST"),
            "PORT": os.environ.get("DB_PORT"),
        },
    }


if ENV == "production":
    redis_url = os.environ.get("REDIS_URL", "").strip()
    if redis_url:
        hosts_redis = [redis_url]
    else:
        redis_host = os.environ.get("REDIS_HOST")
        redis_port = os.environ.get("REDIS_PORT", "6379")
        redis_password = os.environ.get("REDIS_PASSWORD", "")
        if not redis_host:
            raise ImproperlyConfigured("Set REDIS_URL or REDIS_HOST in production.")
        auth = f":{redis_password}@" if redis_password else ""
        hosts_redis = [f"redis://{auth}{redis_host}:{redis_port}/0"]
else:
    hosts_redis = [
        (os.environ.get("REDIS_HOST", "localhost"), os.environ.get("REDIS_PORT", 6379))
    ]


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": hosts_redis},
    },
}


# Config rest_framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_THROTTLE_RATES": {"activation_resend": "5/hour"},
    "DEFAULT_RENDERER_CLASSES": [
        "apps.utils.renderers.CustomJSONRenderer",
    ],
    # 'NON_FIELD_ERRORS_KEY': 'error',
    # 'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    # 'PAGE_SIZE': 2
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
LANGUAGE_CODE = "fr"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)


cloudinary_credentials = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    "API_KEY": os.environ.get("CLOUDINARY_API_KEY", ""),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET", ""),
}
cloudinary_configured = all(cloudinary_credentials.values())

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"
        if ENV == "production" and cloudinary_configured
        else "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if ENV == "production"
        else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

if ENV != "production":
    MEDIA_URL = "/mediafiles/"
    MEDIA_ROOT = os.path.join(BASE_DIR, "mediafiles/")

if ENV == "production" and cloudinary_configured:
    CLOUDINARY_STORAGE = cloudinary_credentials


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "authentication.User"


# Email delivery: use the local console backend when SMTP credentials are absent.
# This keeps account activation testable by printing activation emails in Docker logs.
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True").strip().lower() in {"1", "true", "yes", "on"}
_configured_email_backend = os.environ.get("EMAIL_BACKEND", "").strip()
if _configured_email_backend:
    # Honor an explicit backend selection. In particular, an explicit SMTP
    # setting must not silently fall back to console output when credentials
    # are missing.
    EMAIL_BACKEND = _configured_email_backend
elif EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" if ENV == "development" else "django.core.mail.backends.smtp.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL") or EMAIL_HOST_USER or "webmaster@localhost"
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "15"))


# settings JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=28),
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "public_id",
    "USER_ID_CLAIM": "public_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
}


# the list of origins authorized to make HTTP requests
CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS", "http://localhost:3000 http://127.0.0.1:3000"
).split()

# Domain name frontend

DOMAIN_FRONTEND = os.environ.get("DOMAIN_FRONTEND", "http://localhost:3000")

# Render and other TLS-terminating proxies forward the original HTTPS scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = ENV == "production"
SESSION_COOKIE_SECURE = ENV == "production"
CSRF_COOKIE_SECURE = ENV == "production"
SECURE_CONTENT_TYPE_NOSNIFF = True
if ENV == "production":
    SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000"))


DJANGORESIZED_DEFAULT_SIZE = [500, 500]
# DJANGORESIZED_DEFAULT_SCALE = 0.5
DJANGORESIZED_DEFAULT_QUALITY = 90
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = "JPEG"
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {"JPEG": ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
