# Story Builder

## Purpose Of Project

[edit . 2022-12-04]

- 문제를 만드는 스토리 빌더 입니다.
- 원하는 문제를 만들고 다음 문제로 넘어갈 수 있도록 만드는 재미있는 프로젝트 입니다.

## Project Introduce

[edit . 2022-12-04]

- Story Builder 는 Story 라는 문제지와 Sheet 라는 문제로 구성되어 있습니다.
- Sheet 에 연결되어 있는 정답에 따란 다음 Sheet 로 넘어갑니다.

## Need To Do

- 문제를 해결 했을 경우 아이템 주기
  - 아이템 그룹화
  - 특정 Sheet 에 따른 특정 아이템 줄 수 있도록
  - 아이템 확률
  - 아이템 얻을 때, 뭔가 뺑글뺑글 돌아가면서 아이템 획득하는 것 같은 이팩트

- 이전에 풀었던 문제로 돌아가는 방법
- 가장 최근에 플레이 했던 부분으로 가기 (처음부터, 이어하기 등)

## Project Duration

[edit . 2022-12-04]

2022-11-15 ~ 

## Technologies Used

[edit . 2022-12-04]

#### Framework

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)

#### CI/CD

![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)

#### Database

![MySQL](https://img.shields.io/badge/mysql-%2300f.svg?style=for-the-badge&logo=mysql&logoColor=white) ![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)


## Developer Information

[edit . 2022-12-04]

#### Developer

##### 👨‍🦱 이창우 (Lee Chang Woo)

- Github : https://github.com/cwadven

## Project Structure

[edit . 2022-12-04]

```
Project Root
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

[edit . 2022-12-04]

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

