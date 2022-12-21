from account.models import User


def is_username_exists(username):
    return User.objects.filter(username=username).exists()
