# Django settings for Peoplewings project.
# Those settings are for dev enviroment only.
import os, sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

TEST = 'test' in sys.argv

if TEST:
    # in-memory SQLite used for testing
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            }
        }
else:
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
USE_I18N = False

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
    'peoplewings.apps.dbcontrol',
    'peoplewings.libs.customauth',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

SITE = 'https://0.0.0.0/'
BACKEND_SITE = 'http://0.0.0.0:5000/api/v1/'

# SMTP settings
EMAIL_HOST ='smtp.gmail.com'
EMAIL_HOST_PASSWORD = 'PauVictor2&'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

REGISTER_EMAIL_HOST_USER = 'accounts-noreply@peoplewings.com'
REGISTER_DEFAULT_FROM_EMAIL = 'register-noreply@peoplewings.com'
REGISTER_SERVER_EMAIL = 'PEOPLEWINGS Account New'

FORGOT_EMAIL_HOST_USER = 'accounts-noreply@peoplewings.com'
FORGOT_DEFAULT_FROM_EMAIL = 'accounts-noreply@peoplewings.com'
FORGOT_SERVER_EMAIL = 'PEOPLEWINGS Account Recovery'

NOTIF_EMAIL_HOST_USER = 'accounts-noreply@peoplewings.com'
NOTIF_DEFAULT_FROM_EMAIL = 'noreply@peoplewings.com'
NOTIF_SERVER_EMAIL = 'PEOPLEWINGS'

#IMG
AWS_ACCESS_KEY_ID = "AKIAI5TSJI7DYXGRQDYA"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = "peoplewings-test-media"
AWS_BUCKET_LOCATION = "eu-west-1"

S3_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = S3_URL
MEDIA_URL = 'http://197.168.1.47:5000/media/'

ANONYMOUS_AVATAR = S3_URL + "med-blank_avatar.jpg"
ANONYMOUS_THUMB = S3_URL + "thumb-blank_avatar.jpg"
ANONYMOUS_BLUR = S3_URL + "med-blank_avatar.jpg"
ANONYMOUS_BIG = S3_URL + "blank_avatar.jpg"

LANDSCAPE_PHOTO = S3_URL + "landscape-default.jpg"

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

PROFILE_25 = 10
PROFILE_50 = 25
PROFILE_75 = 50

RECENT_3H = 2000
RECENT_12H = 1000
RECENT_2D = 500
RECENT_1W = 100

AMBASSATOR = 500

BLITLINE_ID = "7XqmahVqL8tvhEIjzBm6-jg"
SRC_BUCKET = "blitline"
DST_BUCKET = AWS_STORAGE_BUCKET_NAME

FB_APP_KEY = '582389231792268'
FB_APP_SECRET = '4f8efdee12534c805baa9071936373b4'