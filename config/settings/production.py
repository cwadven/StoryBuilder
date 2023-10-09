import datetime
from .base import *  # noqa: F401, F403

from .ENV import env_production


DEBUG = False
ALLOWED_HOSTS = ['puzztory.com', 'api.puzztory.com', 'dev-api.puzztory.com']

SECRET_KEY = env_production['SECRET_KEY']
KAKAO_API_KEY = env_production['KAKAO_API_KEY']
KAKAO_SECRET_KEY = env_production['KAKAO_SECRET_KEY']
KAKAO_PAY_API_KEY = env_production['KAKAO_PAY_API_KEY']
KAKAO_PAY_CID = env_production['KAKAO_PAY_CID']
NAVER_API_KEY = env_production['NAVER_API_KEY']
NAVER_SECRET_KEY = env_production['NAVER_SECRET_KEY']
GOOGLE_CLIENT_ID = env_production['GOOGLE_CLIENT_ID']
GOOGLE_SECRET_KEY = env_production['GOOGLE_SECRET_KEY']
GOOGLE_REDIRECT_URL = env_production['GOOGLE_REDIRECT_URL']

AWS_IAM_ACCESS_KEY = env_production['AWS_IAM_ACCESS_KEY']
AWS_IAM_SECRET_ACCESS_KEY = env_production['AWS_IAM_SECRET_ACCESS_KEY']
AWS_S3_BUCKET_NAME = env_production['AWS_S3_BUCKET_NAME']

AWS_SQS_URL = env_production['AWS_SQS_URL']

EMAIL_HOST_USER = env_production['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = env_production['EMAIL_HOST_PASSWORD']

# Slack notification
PUZZTORY_ALERT_SLACK_URL = env_production['PUZZTORY_ALERT_SLACK_URL']

DATABASES = {
    'default': env_production['default']
}

# CacheOps
CACHEOPS_REDIS = env_production['CACHEOPS_REDIS']
CACHEOPS_DEFAULTS = {
    'timeout': 60 * 15
}
CACHEOPS = {
    # 'common.*': {'ops': 'all', 'timeout': 60*15},
    # 'banner.*': {'ops': 'all', 'timeout': 60*15},
    # 'community.*': {'ops': 'all', 'timeout': 60*15},
    # 'tag.*': {'ops': 'all', 'timeout': 60*15},
}

# CELERY SETTINGS
timezone = 'Asia/Seoul'
CELERY_BROKER_URL = 'redis://localhost:6379/1'
result_backend = 'redis://localhost:6379/1'
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',  # redis_server: docker container
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

JWT_AUTH = {
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_ALLOW_REFRESH': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=28),
}
