from account.models import User


def is_username_exists(username):
    return User.objects.filter(username=username).exists()


def is_nickname_exists(nickname):
    return User.objects.filter(nickname=nickname).exists()


def is_email_exists(email):
    return User.objects.filter(email=email).exists()
