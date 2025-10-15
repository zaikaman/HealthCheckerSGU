# Secret loading helper for HealthCheckerSGU
import os
from collections import deque

def load_secrets():
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
    ELEVEN_LABS_API_KEYS = os.environ.get('ELEVEN_LABS_API_KEYS', '')
    ELEVEN_LABS_API_KEYS = ELEVEN_LABS_API_KEYS.split(',') if ELEVEN_LABS_API_KEYS else ['dummy-key-1']
    CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
    CLOUD_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
    CLOUD_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    return {
        'SECRET_KEY': SECRET_KEY,
        'DATABASE_URL': DATABASE_URL,
        'ELEVEN_LABS_API_KEYS': ELEVEN_LABS_API_KEYS,
        'CLOUD_NAME': CLOUD_NAME,
        'CLOUD_API_KEY': CLOUD_API_KEY,
        'CLOUD_API_SECRET': CLOUD_API_SECRET,
        'MAIL_USERNAME': MAIL_USERNAME,
        'MAIL_PASSWORD': MAIL_PASSWORD
    }
