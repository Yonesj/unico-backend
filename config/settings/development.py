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
