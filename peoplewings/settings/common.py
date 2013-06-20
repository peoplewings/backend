# Django settings for Peoplewings project.
import os
import dj_database_url
import subprocess
import imp
import sys
import socket

DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}
PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) # The Django project
PROJECT_DIR = os.path.normpath(os.path.join(PROJECT_ROOT,'..')) # The general project
STATIC_ROOT = os.path.normpath(os.path.join(PROJECT_DIR,'static')) 
MEDIA_ROOT = os.path.normpath(os.path.join(PROJECT_DIR,'media'))
FIXTURE_DIRS = (os.path.join(PROJECT_ROOT, 'general_fixtures'),)
sys.path.append(os.path.normpath(os.path.join(PROJECT_ROOT, 'apps')))



# IMPORT CORRECT SETTINGS BASED IN GIT BRANCHES
LOCAL_HOSTNAMES= ('MacBook-Pro-de-Joan.local', 'Dans-MacBook-Pro.local')
HOSTNAME = socket.gethostname()

def get_environment_file_path(env):
    return os.path.join(PROJECT_ROOT, 'settings', '%s.py' % env)

if 'APP_ENV' in os.environ:
    ENV = os.environ['APP_ENV']
elif HOSTNAME in LOCAL_HOSTNAMES:
    branch = subprocess.check_output(
        ['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip('\n')
    if branch == 'local':
        branch = 'development'
    elif branch == 'development':
        branch = 'testing'
    elif branch == 'stable':
        branch = 'production'
    elif branch == 'alpha':
        branch = 'alpha'

    if os.path.isfile(get_environment_file_path(branch)):
        ENV = branch
    else:
        ENV = 'development'

try:
    config = imp.load_source('env_settings', get_environment_file_path(ENV))
    from env_settings import *    
except IOError:
    exit("No configuration file found for env '%s'" % ENV)
except Exception:
    exit("No env variable found")
## 

TIME_ZONE = 'Europe/Madrid'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.normpath(os.path.join(PROJECT_DIR,'data/media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

# Static content is saved to here --
STATIC_ROOT = os.path.normpath(os.path.join(PROJECT_ROOT,'staticfiles')) # this folder is used to collect static files in production. not used in development
STATIC_ROOT = '/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # "/Users/sergio/Workspace/peoplewings/static/",
    os.path.normpath(os.path.join(PROJECT_DIR, 'data/static')),
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
    'peoplewings.apps.cropper.middleware.Crop',
    'peoplewings.apps.notifications.middleware.Notification',    
    #'peoplewings.libs.middlewares.debug-middleware.DebugMiddleware',
    'peoplewings.libs.middlewares.django-crossdomainxhr-middleware.XsSharing',    
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

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window;

LOGIN_REDIRECT_URL = '/' # url user is redirected after success login
LOGIN_URL = '/login'

# User profiles module
AUTH_PROFILE_MODULE = 'peoplewings.apps.people.UserProfile'

AUTHENTICATION_BACKENDS = ( 
    'peoplewings.apps.people.backends.default.AuthMailBackend',
    'django.contrib.auth.backends.ModelBackend',)

APPEND_SLASH=False
TASTYPIE_ALLOW_MISSING_SLASH = True
SOUTH_TESTS_MIGRATE = False

FB_APP_KEY = '582389231792268'
FB_APP_SECRET = '4f8efdee12534c805baa9071936373b4'
# A place for watchers


