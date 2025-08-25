from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [
    "django_browser_reload",
]

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Static/Media
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATICFILES_DIRS = [BASE_DIR / "static"]
