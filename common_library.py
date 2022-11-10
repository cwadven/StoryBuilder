import string
import uuid
import boto3 as boto3
from random import random
from botocore.config import Config
from botocore.exceptions import ClientError

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import QuerySet, Max
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from rest_framework.exceptions import APIException
from rest_framework_jwt.settings import api_settings
from typing import Optional

from account.models import User
from config.common.exception_codes import PageSizeMaximumException, MissingMandatoryParameterException

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


def mandatory_key(request, name):
    try:
        if request.method == 'GET':
            data = request.GET[name]
        else:
            data = request.POST[name]
        if data in ['', None]:
            raise MissingMandatoryParameterException()
    except:
        try:
            json_body = request.data
            data = json_body[name]
            if data in ['', None]:
                raise MissingMandatoryParameterException()
        except:
            raise MissingMandatoryParameterException()

    return data


# 선택 값
def optional_key(request, name, default_value=''):
    try:
        if request.method == 'GET':
            data = request.GET[name]
        else:
            data = request.POST[name]
        if data in ['', None]:
            data = default_value
    except:
        try:
            json_body = request.data
            data = json_body[name]
            if data in ['', None]:
                data = default_value
        except:
            data = default_value
    return data


def paging(request: HttpRequest, default_size: int = 10) -> tuple:
    try:
        page = int(request.GET.get('page', 1)) - 1
        size = int(request.GET.get('size', default_size))
        if size > 30:
            raise PageSizeMaximumException()
        start_row = page * size
        end_row = (page + 1) * size
    except APIException as e:
        raise APIException(e)
    return start_row, end_row


def get_login_token(user: User) -> str:
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    return token


def get_max_int_from_queryset(qs: QuerySet, field_name: str) -> Optional[int]:
    return qs.aggregate(_max=Max(field_name)).get('_max')


def get_request_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def generate_presigned_url(file_name, _type='common', unique=0, expires_in=1000):
    s3_client = boto3.client(
        's3',
        region_name='ap-northeast-2',
        aws_access_key_id=settings.AWS_IAM_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_IAM_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4')
    )
    try:
        response = s3_client.generate_presigned_post(
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=f'{_type}/{unique}/{uuid.uuid4()}_{file_name}',
            ExpiresIn=expires_in
        )
        return response
    except ClientError as e:
        return None


def upload_file_to_presigned_url(presined_url, presigned_data, file):
    try:
        response = requests.post(
            url=presined_url,
            data=presigned_data,
            files={'file': file}
        )
        return response.status_code
    except:
        return 400


def send_email(title: str, html_body_content: str, payload: dict, to: list) -> None:
    """
    title: 메일 제목
    html_body_content: 적용할 templates 폴더에 있는 html 파일 위치
    payload: 해당 template_tag 로 쓰일 값들
    to: 보낼 사람들 (리스트로 전달 필요)
    """
    message = render_to_string(
        html_body_content,
        payload
    )
    send_mail(
        title,
        strip_tags(message),
        settings.EMAIL_HOST_USER,
        to,
        html_message=message,
        fail_silently=False,
    )


def generate_random_string_digits(length: int = 4) -> str:
    """랜덤한 ascii_letters or digits 를 합성하여 _length 길이만큼 생성한다.
    예) QD5M9hGo2i => _length = 10

    :param length: int
    :return: str
    """
    return ''.join(random.choice(string.digits) for _ in range(length))
