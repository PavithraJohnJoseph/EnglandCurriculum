import os
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

DEBUG = os.environ.get("DEBUG", "False") == "True"

# Parse comma-separated ALLOWED_HOSTS from environment
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# ===============================
# INSTALLED APPS
# ===============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'core',
]

AUTH_USER_MODEL = 'core.User'


# ===============================
# MIDDLEWARE
# ===============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'core.middleware.EmailVerificationRequiredMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'phonics_app.urls'


# ===============================
# TEMPLATES
# ===============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "core/templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'phonics_app.wsgi.application'


# ===============================
# DATABASE CONFIGURATION
# ===============================
# Support both SQLite and PostgreSQL based on DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./db.sqlite3")

if DATABASE_URL.startswith("postgresql://"):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    # SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ===============================
# PASSWORD VALIDATION
# ===============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ===============================
# INTERNATIONAL
# ===============================
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True


# ===============================
# STATIC FILES
# ===============================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "core/static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ===============================
# LOGIN REDIRECTS
# ===============================
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'core:login'

# ===============================
# SECURITY SETTINGS - PRODUCTION
# ===============================
# Default security posture is based on DEBUG, but every setting can be overridden
# via environment variables for local/prod flexibility.

SECURE_SSL_REDIRECT = os.environ.get("SECURE_SSL_REDIRECT", "True" if not DEBUG else "False") == "True"
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "True" if not DEBUG else "False") == "True"
# Always set CSRF_COOKIE_SECURE = False in development for local HTTP, True in production for HTTPS
if DEBUG:
    CSRF_COOKIE_SECURE = False
else:
    CSRF_COOKIE_SECURE = os.environ.get("CSRF_COOKIE_SECURE", "True") == "True"
SECURE_HSTS_SECONDS = int(os.environ.get("SECURE_HSTS_SECONDS", "31536000" if not DEBUG else "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True" if not DEBUG else "False") == "True"
SECURE_HSTS_PRELOAD = os.environ.get("SECURE_HSTS_PRELOAD", "True" if not DEBUG else "False") == "True"
SECURE_BROWSER_XSS_FILTER = os.environ.get("SECURE_BROWSER_XSS_FILTER", "True" if not DEBUG else "False") == "True"

if not DEBUG:
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'"),
        'style-src': ("'self'", "'unsafe-inline'"),
    }

# Prevent localhost vs 127.0.0.1 origin mismatches during local development.
CSRF_TRUSTED_ORIGINS = os.environ.get(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:8000,http://127.0.0.1:8000",
).split(",")

# ===============================
# EMAIL CONFIGURATION
# ===============================
# Email Backend Configuration
# Use SMTP if credentials are provided, otherwise console backend
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    # Use SMTP when credentials are configured
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
else:
    # Fallback to console backend (prints emails to terminal)
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    print("⚠️  WARNING: Email credentials not configured. Emails will print to console.")
    print("   Set EMAIL_HOST_USER and EMAIL_HOST_PASSWORD environment variables to send real emails.")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@phonicsapp.com")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "server@phonicsapp.com")

# Site URLs for email links
SITE_URL = os.environ.get("SITE_URL", "http://localhost:8000")
SITE_NAME = os.environ.get("SITE_NAME", "Year 1 Phonics")

# ===============================
# STRIPE CONFIGURATION
# ===============================
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Stripe callback URLs
STRIPE_CALLBACK_SUCCESS_URL = os.environ.get(
    "STRIPE_CALLBACK_SUCCESS_URL",
    "http://localhost:8000/years/"
)
STRIPE_CALLBACK_CANCEL_URL = os.environ.get(
    "STRIPE_CALLBACK_CANCEL_URL",
    "http://localhost:8000/plans/"
)

# ===============================
# PRACTICE PAGE THEME
# ===============================
_default_page_colors = [
    "#8A2BE2",  # Violet
    "#4B0082",  # Indigo
    "#1E90FF",  # Blue
    "#2E8B57",  # Green
    "#FF8C00",  # Orange
    "#8A2BE2",  # Violet
    "#4B0082",  # Indigo
    "#1E90FF",  # Blue
    "#2E8B57",  # Green
    "#FF8C00",  # Orange
]

PAPER_PAGE_COLOR_CYCLE = [
    c.strip()
    for c in os.environ.get("PAPER_PAGE_COLOR_CYCLE", ",".join(_default_page_colors)).split(",")
    if c.strip()
]