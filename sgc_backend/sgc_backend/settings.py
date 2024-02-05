"""
Django settings for sgc_backend project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from datetime import timedelta
import datetime
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-loh-r&2+n&c&mmf(hcvdn@f51gc8m(k9k4=(=-s@j5x2$gaf%k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
##multiple workers celery -A your_project_name worker --loglevel=info -n worker1@%h
#remember to install redis
#CELERY_BROKER_URL = 'amqp://fssgc:fssgc@192.168.169.23:15672//'
#BROKER_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@192.168.169.23:15672/')
CELERY_BROKER_URL = 'amqp://fssgc:fssgc@localhost'
CELERY_TASK_RESULT_EXPIRES = None
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_TASK_IGNORE_RESULT = False
#CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
INSTALLED_APPS = [    
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'public.apps.PublicConfig',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'rest_framework.authtoken',
    'drf_yasg',
    'fidecomisos',
    'actores_de_contrato_cargue',
    'beneficiario_final',
    'Log_Changes',
    'django_celery_beat',
    'django_celery_results'
    
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",    
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'sgc_backend.middleware.CurrentRequestMiddleware'
   
    
]
SHELL_PLUS = "ipython"
ROOT_URLCONF = 'sgc_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'sgc_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.oracle",
        "NAME": "xe",
        "USER": "SGC_SOFTWARE_DEV_F",
        "PASSWORD": "SGC_SOFTWARE_DEV_F",
        "HOST": "localhost",
        "PORT": "1522",
    },
    "sifi":{
        "NAME": "SIFIVAL",
        "ENGINE": "django.db.backends.oracle",
        "USER": "VU_SFI",
        "PASSWORD": "VU_SFI",
        "HOST":"192.168.168.175",
        "PORT": "1521",
    },
    "sgc":{
        "NAME": "SIFIVAL",
        "ENGINE": "django.db.backends.oracle",
        "USER": "FS_SGC_US",
        "PASSWORD": "FS_SGC_US",
        "HOST":"192.168.168.175",
        "PORT": "1521",
    }
    
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SIMPLE_JWT = {
    # It will work instead of the default serializer(TokenObtainPairSerializer).
    "TOKEN_OBTAIN_SERIALIZER": "accounts.serializers.MyTokenObtainPairSerializer",
    # ...
}
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

JWT_AUTH = {
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=36000),
}
#LOGIN_REDIRECT_URL='/'

CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
    "http://localhost:4200",
    "http://127.0.0.1:9000",
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]