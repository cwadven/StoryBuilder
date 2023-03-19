import re
from account.models import User


def is_username_exists(username):
    return User.objects.filter(username=username).exists()


def is_nickname_exists(nickname):
    return User.objects.filter(nickname=nickname).exists()


def is_email_exists(email):
    return User.objects.filter(email=email).exists()


def is_email_reg_exp_valid(email):
    return re.match(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)


def is_length_valid(string, min_length, max_length):
    return min_length <= len(string) <= max_length


def is_only_alphanumeric(string):
    return re.match(r'^[a-zA-Z0-9]+$', string)


def is_only_korean_english_alphanumeric(string):
    return re.match(r'^[ㄱ-ㅎ가-힣a-zA-Z0-9]+$', string)
