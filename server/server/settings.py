import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root (one level above server/)
load_dotenv(BASE_DIR.parent / '.env')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'corsheaders',
    'events',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'server.urls'

WSGI_APPLICATION = 'server.wsgi.application'

META_ACCESS_TOKEN = os.environ.get('META_ACCESS_TOKEN', '')
META_PIXEL_ID = os.environ.get('META_PIXEL_ID', '2881174115331441')

TIKTOK_ACCESS_TOKEN = os.environ.get('TIKTOK_ACCESS_TOKEN', '')
TIKTOK_PIXEL_ID = os.environ.get('TIKTOK_PIXEL_ID', 'D6B1UFJC77U56TVAO8RG')

REDDIT_ACCESS_TOKEN = os.environ.get('REDDIT_ACCESS_TOKEN', '')
REDDIT_PIXEL_ID = os.environ.get('REDDIT_PIXEL_ID', 'a2_ibjroms8g8bo')
