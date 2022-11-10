from django.contrib.auth import user_logged_in
from django.test import Client


class LoginMixin(object):
    def login(self) -> Client:
        user_logged_in.receivers = []
        # user = User.objects.create_user(username='1111', email='testtest@naver.com')
        # self.c._login(user)
        # self.c.user = user

    # def setUp(self):
    #     self.c = Client()
