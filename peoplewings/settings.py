# Django settings for Peoplewings project.
import os
import dj_database_url
DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}


DEBUG = True
TEMPLATE_DEBUG = DEBUG

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # The Django project
PROJECT_DIR = os.path.normpath(os.path.join(PROJECT_ROOT,'..')) # The genral project

ADMINS = (
    #('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'd9v8pn437eoleu',        # Or path to database file if using sqlite3.
        'USER': 'tbkwhgpiyhvhnv',        # Not used with sqlite3.
        'PASSWORD': 'rGxtOjErcyAxNbEJZx4RNjUw3T',           # Not used with sqlite3.
        'HOST': 'ec2-23-21-85-197.compute-1.amazonaws.com', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.
    }
}

"""
FIXTURE_DIRS = (
    os.path.normpath(os.path.join(PROJECT_ROOT,'/people/fixtures/')),
)
"""

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.normpath(os.path.join(PROJECT_DIR,'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

# Static content is saved to here --
STATIC_ROOT = os.path.normpath(os.path.join(PROJECT_ROOT,'staticfiles')) # this folder is used to collect static files in production. not used in development
STATIC_URL =  "/static/"

#STATIC_ROOT = '/static_media/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
#STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # "/Users/sergio/Workspace/peoplewings/static/",
    os.path.normpath(os.path.join(PROJECT_DIR, 'static')),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '1uon%$p0+qvkuy(w=m-kuydmon$sh3@1wq^x5mxo2v5uwh1=gl'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'peoplewings.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'peoplewings.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # Cross-platform stylish TEMPLATE_DIRS definition
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)

INSTALLED_APPS = (
    'gunicorn',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'landing',
    'registration',
    'people',
    #'south',
    'ajax',
    'wings',
    'cropper',
    #'imagekit',
    'search',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

#CROPPER_ROOT = MEDIA_ROOT

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window;

# SMTP settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'peoplewings.dev@gmail.com'
EMAIL_HOST_PASSWORD = 'wings208b'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

LOGIN_REDIRECT_URL = '/' # url user is redirected after success login
LOGIN_URL = '/login'

# User profiles module
AUTH_PROFILE_MODULE = 'people.UserProfile'

AUTHENTICATION_BACKENDS = ( 
    'people.backends.default.AuthMailBackend',
    'django.contrib.auth.backends.ModelBackend',)

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

if DEBUG:
    try:
	    from settings_ezequiel import *
    except ImportError:
	    pass
		


# A place for watchers
"""
print "PROJECT_ROOT: " + PROJECT_ROOT
print "PROJECT_DIR: " + PROJECT_DIR
print "STATICFILES_DIRS: " + STATICFILES_DIRS[0]
print "STATIC_ROOT: " + STATIC_ROOT
print "STATIC_URL: " + STATIC_URL
"""

