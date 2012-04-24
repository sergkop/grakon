# Django settings for grakon project.

TIME_ZONE = 'Europe/Moscow'

LANGUAGE_CODE = 'ru-RU'

SITE_ID = 1

USE_I18N = True
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = ()

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',

    'grakon.context_processors.media_files',
    'grakon.context_processors.project_settings',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.ProfileMiddleware',
)

ROOT_URLCONF = 'grakon.urls'

WSGI_APPLICATION = 'grakon.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    # Libraries
    'crispy_forms',
    'social_auth',
    'south',
    'tinymce',

    # Applications
    'elements',
    'users',
    'authentication',
    'grakon',
    'locations',
    'navigation',
)

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

AUTH_PROFILE_MODULE = 'users.Profile'
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/profile' # must be the same as reverse('profile')
#LOGIN_ERROR_URL    = '/login-error/'

SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/social_registration' # the same as reverse('social_registration')

SOCIAL_AUTH_PIPELINE = (
    'social_auth.backends.pipeline.social.social_auth_user',
    'social_auth.backends.pipeline.associate.associate_by_email',
    'social_auth.backends.pipeline.user.get_username',

    'social_auth.backends.pipeline.misc.save_status_to_session',
    'authentication.views.social_registration_pipeline',

    #'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    'social_auth.backends.pipeline.social.load_extra_data',
    #'social_auth.backends.pipeline.user.update_user_details'
)

SOCIAL_AUTH_PIPELINE_RESUME_ENTRY = 'social_auth.backends.pipeline.user.create_user'

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
    'authentication.backend.EmailAuthenticationBackend',
)

from grakon.site_settings import *

TINYMCE_JS_URL = STATIC_URL + 'libs/tiny_mce/tiny_mce.js'
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, 'libs', 'tiny_mce')
TINYMCE_DEFAULT_CONFIG = {
    'theme': 'advanced',
    'relative_urls': False,
    'width': '100%',
    'height': 300,
    'theme_advanced_buttons1': "bold,italic,underline,strikethrough,|,fontsizeselect",
    'theme_advanced_buttons2': "bullist,numlist,|,outdent,indent,|,undo,redo,|,link,unlink,code",
    'theme_advanced_buttons3': ",fontselect,|,charmap",
    'extended_valid_elements': "script[type|src],iframe[src|style|width|height|scrolling|marginwidth|marginheight|frameborder],",
}
TINYMCE_COMPRESSOR = False # TODO: compression doesn't work at the moment

CRISPY_TEMPLATE_PACK = 'uni_form'

# force removal of mysite.fcgi from URL (needed for fastcgi deployment)
# http://docs.djangoproject.com/en/dev/howto/deployment/fastcgi/#forcing-the-url-prefix-to-a-particular-value
FORCE_SCRIPT_NAME = ''

# Numbers of entries shown in the side blocks for tools and participants
TOP_FOLLOWERS_COUNT = 3
TOP_FOLLOWED_COUNT = 3
TOP_PARTICIPANTS_COUNT = 7 # number of participants displayed on location page
