import json

from django.test import TestCase
from django.urls import reverse

from config.test_helper.helper import LoginMixin
from point.models import UserPoint


class UserPointAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(UserPointAPIViewTestCase, self).setUp()

    def test_get_user_point_api(self):
        # Given: User 에게 10 포인트 지급
        self.login()
        point = 10
        UserPoint.objects.create(
            user_id=self.c.user.id,
            point=point,
            description='test',
        )

        # When: user_point_info 요청
        response = self.c.get(reverse('point:user_point_info'))
        content = json.loads(response.content)

        # Then: total_point 조회
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['total_point'], point)
