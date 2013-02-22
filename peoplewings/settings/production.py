# Django settings for Peoplewings project.
# Those settings are for production enviroment only.
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'derpr1u0brbo6h',                      # Or path to database file if using sqlite3.
        'USER': 'paucbpbuauurig',                      # Not used with sqlite3.
        'PASSWORD': '5UACWRXRwmjhlWsvBEpgn2C61y',                  # Not used with sqlite3.
        'HOST': 'ec2-23-21-209-85.compute-1.amazonaws.com',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

INSTALLED_APPS = (
    # Standard django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # Installed external apps
    'gunicorn',
    'south',
    'tastypie',
    'storages',
    # Project custom apps
    'peoplewings.apps.landing',
    'peoplewings.apps.registration',
    'peoplewings.apps.people',
    'peoplewings.apps.ajax',
    'peoplewings.apps.wings',
    'peoplewings.apps.cropper',
    'peoplewings.apps.search',
    'peoplewings.apps.locations',
    'peoplewings.apps.feedback',
    'peoplewings.libs.customauth',
    'peoplewings.libs.S3Custom',

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# SMTP settings
EMAIL_HOST = 'smtp.1and1.es' #probar con .com
EMAIL_HOST_USER = 'emailconfirm@peoplewings.com'
EMAIL_HOST_PASSWORD = 'wings208b'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'emailconfirm@peoplewings.com'
SERVER_EMAIL = 'emailconfirm@peoplewings.com'

#SITE
SITE = 'http://peoplewings.herokuapp.com'
BACKEND_SITE = 'https://peoplewings-backend-stable.herokuapp.com/api/v1/'

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

#IMG
AWS_ACCESS_KEY_ID = "AKIAI5TSJI7DYXGRQDYA"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = "peoplewings-test-media"

S3_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL
MEDIA_URL = 'https://peoplewings-backend-stable.herokuapp.com/media/'

ANONYMOUS_AVATAR = S3_URL + "med-blank_avatar.jpg"
ANONYMOUS_THUMB = S3_URL + "thumb-blank_avatar.jpg"
ANONYMOUS_BLUR = S3_URL + "med-blank_avatar.jpg"
ANONYMOUS_BIG = S3_URL + "blank_avatar.jpg"

# Storages IMG
AWS_QUERYSTRING_AUTH = False
LOGIN_TIME = 3600
