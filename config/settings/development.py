import os
from .base import *


DEBUG = True

SECRET_KEY = 'django-insecure-1wpof=ecqs@udx#m=fq+xqd7shb6+58c_!!x#v5h-n2j9#apcj'

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DEV_DB_NAME', 'unico_dev_db'),
        'USER': os.getenv('DEV_DB_USER', 'unico_dev_user'),
        'PASSWORD': os.getenv('DEV_DB_PASSWORD', 'unico'),
        'HOST': os.getenv('DEV_DB_HOST', 'db'),
        'PORT': os.getenv('DEV_DB_PORT', '5432'),
    }
}

INTERNAL_IPS = [
    '127.0.0.1',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "unico.test2@gmail.com"
EMAIL_HOST_PASSWORD = "dflt jetp fcua mnyg"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

PASSWORD_RESET_URL = "http://localhost:3000/reset-password"
