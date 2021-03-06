# Django settings for gridcontrol project.
import os
import djcelery

djcelery.setup_loader()

ROOT = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
		'default': {
				'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
				'NAME': os.path.join(ROOT, 'db.sqlite3'),											# Or path to database file if using sqlite3.
				'USER': '',
				'PASSWORD': '',
				'HOST': '',											# Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
				'PORT': '',											# Set to empty string for default.
		}
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'HST'

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
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(ROOT, 'static_cache')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
		# Put strings here, like "/home/html/static" or "C:/www/django/static".
		# Always use forward slashes, even on Windows.
		# Don't forget to use absolute paths, not relative paths.
		os.path.join(ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
		'django.contrib.staticfiles.finders.FileSystemFinder',
		'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#		'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
		'django.template.loaders.filesystem.Loader',
		'django.template.loaders.app_directories.Loader',
#		 'django.template.loaders.eggs.Loader',
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

ROOT_URLCONF = 'gridcontrol.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'gridcontrol.wsgi.application'

TEMPLATE_DIRS = (
		# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
		# Always use forward slashes, even on Windows.
		# Don't forget to use absolute paths, not relative paths.
		os.path.join(ROOT, 'templates'),
)

INSTALLED_APPS = (
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.sites',
		'django.contrib.messages',
		'django.contrib.staticfiles',
		'django.contrib.admin',
		'south',
		'djcelery',
		'social_auth',
		'gridcontrol.content',
		'gridcontrol.engine',
)

AUTHENTICATION_BACKENDS = (
	'social_auth.backends.contrib.github.GithubBackend',
	'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL		  = '/login-form/'
LOGIN_REDIRECT_URL = '/logged-in/'
LOGIN_ERROR_URL	= '/login-error/'

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

from celery.schedules import crontab
from datetime import timedelta

CELERYBEAT_SCHEDULE = {
	"game_tick": {
		"task": "gridcontrol.engine.tick_all_users",
		"schedule" : crontab(minute='*/1'),
		"args": None,
	},
}

CELERY_TASK_PUBLISH_RETRY_POLICY = {
	'max_retries': None,
	'interval_start': 60 * 5,
	'interval_step': 60,
	'interval_max': 60 * 30,
}

CELERYD_NODES = "w1 w2 w3"

SECRET_KEY = 'lolthisisnotmysecret'
BROKER_URL = 'redis://localhost:6379/0' # 0 is for celery
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
GITHUB_APP_ID = 'lolmyappid'
GITHUB_API_SECRET = 'lolmyapisecret'

ENGINE_BROKER_HOST = 'localhost'
ENGINE_BROKER_PORT = 6379
ENGINE_BROKER_DB = 1

GRIDCONTROL_LINE_LIMIT = 1000
GRIDCONTROL_CONST_LIMIT = 500
GRIDCONTROL_DATA_LIMIT = 500
GRIDCONTROL_EXE_LIMIT = 500
GRIDCONTROL_REG_LIMIT = 500

GRIDCONTROL_GIST_MAX_SIZE = 500 * 1024

GRIDC_COMPILER_URI = 'http://lessandro.com/gridc-ws/'
