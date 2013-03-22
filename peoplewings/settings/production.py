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
USE_I18N = False

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
    'compressor',       
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
    'peoplewings.apps.notifications',

    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

# Storages IMG
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'

#SITE
SITE = 'https://peoplewings-frontend.s3-website-eu-west-1.amazonaws.com/'
BACKEND_SITE = 'https://peoplewings-backend-stable.herokuapp.com/api/v1/'
# SMTP settings
EMAIL_HOST = 'smtp.1and1.es' #probar con .com
EMAIL_HOST_USER = 'emailconfirm@peoplewings.com'
EMAIL_HOST_PASSWORD = 'wings208b'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'emailconfirm@peoplewings.com'
SERVER_EMAIL = 'emailconfirm@peoplewings.com'

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

PHOTO_SCORE = 5
MAX_UPLOADED_PHOTOS = 25
REPLY_RATE_100 = 500
REPLY_RATE_90 = 400
REPLY_RATE_80 = 300
REPLY_RATE_70 = 100
REPLY_RATE_60 = 50
REPLY_RATE_50 = 25
REPLY_RATE_sub50 = 0 

REPLY_TIME_1H = 500
REPLY_TIME_4H = 400
REPLY_TIME_12H = 300
REPLY_TIME_24H = 100
REPLY_TIME_48H = 50
REPLY_TIME_1W = 25
REPLY_TIME_super1W = 0

POPULARITY_24H_0 = 500
POPULARITY_24H_1 = 500
POPULARITY_24H_5 = -250
POPULARITY_24H_10 = -500
POPULARITY_24H_15 = -750
POPULARITY_24H_20 = -1000
POPULARITY_24H_super20 = -1000

POPULARITY_1W_0 = 750
POPULARITY_1W_5 = 250
POPULARITY_1W_10 = 100
POPULARITY_1W_15 = 0
POPULARITY_1W_20 = -100
POPULARITY_1W_25 = -250
POPULARITY_1W_30 = -500
POPULARITY_1W_50 = -750
POPULARITY_1W_70 = -1000
