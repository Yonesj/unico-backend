import os
from .base import *


DEBUG = False

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-1wpof=ecqs@udx#m=fq+xqd7shb6+58c_!!x#v5h-n2j9#apcj')

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PROD_DB_NAME'),
        'USER': os.getenv('PROD_DB_USER'),
        'PASSWORD': os.getenv('PROD_DB_PASSWORD'),
        'HOST': os.getenv('PROD_DB_HOST'),
        'PORT': os.getenv('PROD_DB_PORT'),
    }
}
