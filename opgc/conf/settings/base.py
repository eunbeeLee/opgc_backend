# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',

    'apps.users',
    'apps.githubs',
    'apps.reservations',

    'corsheaders'
]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'OPGC_SECRET_KEY'

# Gihub api auth token
OPGC_TOKEN = 'OPGG_GITHUB_TOKEN'
