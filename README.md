# NULLYS DjangoRESTFramework TEMPLATE

## Purpose Of Project

[edit . 2022-02-09]

- Django DRF 용 TEMPLATE

## Project Introduce

[edit . 2022-08-07]

- Github Clone 으로 DRF 프로젝트를 빠르게 생성하기 위한 Template
- 비동기 처리 Celery
- 캐시 서버 Redis Cacheops
- Random Model Object Create
- CI/CD Github Actions
- TestCase Github Actions
- 회원 및 소셜 로그인 기능 제공 (카카오, 네어버, 구글)

## Project Duration

[edit . 2022-08-05]

2022-02-09 ~ 

## Technologies Used

[edit . 2022-08-07]

#### Framework

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)

#### CI/CD

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

#### Database

![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white) ![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)

#### Others

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)


## Developer Information

[edit . 2022-02-09]

#### Developer

##### 👨‍🦱 이창우 (Lee Chang Woo)

- Github : https://github.com/cwadven

## Project Structure

[edit . 2022-02-09]

```
Project Root
├── 📂 docker
│    └── 📂 mysql_server
│         ├── 📂 log
│         ├── 📂 data
│         └── 📂 conf.d
│              └── 📜 my.cnf
│
├── 📂 config
│    ├── 📂 settings
│    │    ├── 📜 base.py
│    │    ├── 📜 development.py
│    │    ├── 📜 production.py
│    │    └── 📜 ENV.py  
│    │
│    ├── 📂 test_helper
│    │    └── 📜 helper.py  
│    │
│    ├── 📂 middleware
│    │    └── 📜 api_extension.py
│    │
│    ├── 📂 authorization
│    │    └── 📜 authentication.py
│    │
│    ├── 📂 common
│    │    ├── 📜 enums.py
│    │    └── 📜 response_codes.py  
│    │
│    ├── 📜 celery.py
│    ├── 📜 asgi.py
│    ├── 📜 urls.py
│    └── 📜 wsgi.py
│
├── 📂 pre_setting
│    ├── 📂 migrations                                                      
│    └── 📂 management
│         └── 📂 commands  
│              ├── 📜 createrandom.py  # 랜덤한 데이터 생성용 Command
│              └── 📜 gitaction.py     # GitAction 설정용 Command
│                                    
├── 📂 App Name
│    ├── 📂 migrations
│    ├── 📂 test              
│    │    └── 📂 view_tests.py
│    │                      
│    ├── 📜 admin.py                                  
│    ├── 📜 app.py
│    ├── 📜 forms.py
│    ├── 📜 urls.py
│    ├── 📜 views.py
│    └── 📜 models.py  
│  
├── 📂 App Name
│    ├── 📂 migrations                                     
│    ├── 📜 admin.py                                  
│    ├── 📜 app.py
│    ├── 📜 forms.py
│    └ .....
│
├── 📂 temp_static
│    ├── 🖼 XXXXX.png                                     
│    ├── 🖼 XXXXX.png                                  
│    ├── 🖼 XXXXX.png
│    ├── 🖼 XXXXX.png
│    └ .....
│
├── 📂 templates
│    └── base.html    
│
├── 📜 common_library.py
├── 📜 common_decorator.py
├── 📜 manage.py
├── 📜 redis-server.yml
├── 📜 mysql-server.yml
├── 📋 command.cron                                      # cron
├── 🗑 .gitignore                                        # gitignore
├── 🗑 requirements.txt                                  # requirements.txt
└── 📋 README.md                                        # Readme
```

## Usage

[edit . 2022-08-05]

## With Docker

Docker 설정을 하지 않을 경우 바로 밑에 `기본설정` 부터 가이드를 따르세요!

---

```shell
# MySQL 실행
docker-compose -f docker/mysql-server.yml up -d

# Redis 실행
docker-compose -f docker/redis-server.yml up -d
```

#### 데이터베이스 설정
```shell
# mysql 도커 cli 실행 후 mysql 초기 접속
mysql -u root -p
비밀번호 root

# 데이터베이스 생성
CREATE DATABASE 데이터베이스명;

# 루트 비밀번호 변경
# mysql 8.0 이상은 mysql_native_password 로 비밀변호 생성 필요
ALTER user 'root'@'%' IDENTIFIED WITH mysql_native_password BY '변경 비밀번호';
FLUSH PRIVILEGES;

# settings 폴더에 있는 python 파일에 비밀번호 수정
```


### 1. 기본 설정

#### 1. config/settings 폴더에 `ENV.py` 파일 생성 후 아래와 같이 정의

#### ENV.py 틀
```python
env_production = {
    'SECRET_KEY': 'django_secret_key',
    'KAKAO_API_KEY': 'kakao_api_key',
    'KAKAO_SECRET_KEY': 'kakao_secret_key',
    'CHANNEL_LAYERS': {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [('127.0.0.1', 6379)],
            },
        },
    },
    'CACHEOPS_REDIS': {
        'host': 'localhost',
        'port': 6379,
        'db': 10,
    },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '데이터베이스명',
        'USER': 'root',
        'PASSWORD': 'root(초기도커설정)',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
        'TEST': {
            'NAME': 'test_데이터베이스명',
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        }
    },
    'EMAIL_HOST_USER': '이메일주소@주소.com',
    'EMAIL_HOST_PASSWORD': '이메일비밀번호',
    'AWS_IAM_ACCESS_KEY': 'IAMACCESSKEY',
    'AWS_IAM_SECRET_ACCESS_KEY': 'IAMSECRETACCESSKEY',
    'AWS_S3_BUCKET_NAME': 'S3BUCKETNAME',
}

env_development = {
    ...
}
```

#### 2. 환경 변수 설정

```shell
# production 설정
export DJANGO_SETTINGS_MODULE=config.settings.production
```

만약 설정을 하지 않은 경우 settings 는 development.py 를 바라봅니다.

### 2. temp_static 폴더 프로젝트 폴더에 생성

- collectstatic 위한 의존성 폴더 생성

### 3. 서버 초기 설정

```shell
python manage.py migrate
```

```shell
python manage.py collectstatic --no-input
```

### 4. 서버 실행

```shell
python manage.py runserver
```

### 5. celery 세팅
```shell
# redis 설치 필요
celery -A config worker --loglevel=INFO --pool=solo
```

### ETC.

#### 1. Django 테스트 케이스 실행

Pycharm 혹은 shell 을 이용할 때 settings 파일 경로를 환경변수에 설정 합시다.
`--keepdb` 를 사용하지 않으면 디비를 지웠다가 생성합니다. 

```shell
python manage.py test --keepdb
```

아래와 같은 에러가 나올 경우 
```shell
Got an error creating the test database: (1044, "Access denied for user 'XXX'@'localhost' to database ...
```

database 에 접속하여 해당 데이터베이스에 접근할 수 있는 권한을 줍니다.

```mysql
GRANT ALL PRIVILEGES ON 테스트데이터베이스명.* TO `유저명`@`localhost`;
FLUSH PRIVILEGES;
```

<br>

#### 2. 랜덤 데이터 추가

- postgresql 다운로드 필요 (psycopg2 때문... mac 경우 - psycopg2-binary)

```shell
python manage.py createrandom 앱명 테이블명 (option -n "생성숫자")

# 예제
python manage.py createrandom crud Product -n 7
```

