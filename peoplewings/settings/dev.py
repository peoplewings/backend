# Django settings for Peoplewings project.
# Those settings are for dev enviroment only.
from common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'postgres',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': '1111',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

INSTALLED_APPS = (
    # Standard django apps
    'django.contrib.auth', #User django auth
    'django.contrib.contenttypes', #User django auth
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Installed external apps
    'gunicorn',
    'south',
    'tastypie',
    # Project custom apps
    'peoplewings.apps.registration',
    'peoplewings.apps.landing',
    'peoplewings.apps.people',
    'peoplewings.apps.ajax',
    'peoplewings.apps.wings',
    'peoplewings.apps.cropper',
    'peoplewings.apps.search',
    'peoplewings.apps.locations',
    'peoplewings.apps.notifications',
    'peoplewings.apps.feedback',
    'peoplewings.libs.customauth',    
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

SITE = 'http://peoplewings-frontend.herokuapp.com'

# SMTP settings
EMAIL_HOST = 'smtp.1and1.es' #probar con .com
EMAIL_HOST_USER = 'emailconfirm@peoplewings.com'
EMAIL_HOST_PASSWORD = 'wings208b'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'developers@peoplewings.com'
SERVER_EMAIL = 'developers@peoplewings.com'
"""
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'peoplewings.dev@gmail.com'
EMAIL_HOST_PASSWORD = 'wings208b'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
"""

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#IMG
MEDIA_ROOT = '/data/media/'
STATIC_ROOT = '/data/static/'

AWS_ACCESS_KEY_ID = "AKIAI5TSJI7DYXGRQDYA"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = "peoplewings-test-media"

S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL
MEDIA_URL = S3_URL

ANONYMOUS_AVATAR = S3_URL + "med-blank_avatar.jpg"
"""
# Compressor IMG
COMPRESS_ENABLED = True
if COMPRESS_ENABLED:
    COMPRESS_CSS_FILTERS = [
        'compressor.filters.css_default.CssAbsoluteFilter',
        'compressor.filters.cssmin.CSSMinFilter',
    ]
    COMPRESS_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    COMPRESS_URL = STATIC_URL
    COMPRESS_OFFLINE = True
"""
# Storages IMG
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_QUERYSTRING_AUTH = False
