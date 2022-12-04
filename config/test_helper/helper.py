from django.contrib.auth import user_logged_in
from django.test import Client

from account.models import User


class LoginMixin(object):
    def login(self, user=None):
        user_logged_in.receivers = []
        if not user:
            user = User.objects.create_user(username='1111', email='testtest@naver.com')
        self.c._login(user)
        self.c.user = user

    def setUp(self):
        self.c = Client()
