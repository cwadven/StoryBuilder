from django.test import TestCase

from account.models import User
from config.common.exception_codes import NotEnoughUserPoints
from config.test_helper.helper import LoginMixin
from point.models import UserPoint
from point.services import get_user_available_total_point, use_point


class UserPointTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(UserPointTestCase, self).setUp()
        self.user = User.objects.all()[0]

    @staticmethod
    def _give_user_points(user, point):
        return UserPoint.objects.create(
            user=user,
            point=point,
            description='test 포인트 지급',
        )

    def test_get_user_available_total_point(self):
        # Given: Point 2번 각각 지급
        self._give_user_points(self.user, 100)
        self._give_user_points(self.user, 200)

        # When:
        total_point = get_user_available_total_point(self.user.id)

        # Then:
        self.assertEqual(total_point, 300)

    def test_get_user_available_total_point_when_point_is_minus(self):
        # Given: Point 2번 각각 지급 (마이너스 값)
        self._give_user_points(self.user, 100)
        self._give_user_points(self.user, -200)

        # When:
        total_point = get_user_available_total_point(self.user.id)

        # Then: 0 반환
        self.assertEqual(total_point, 0)

    def test_get_user_available_total_point_when_point_is_not_active(self):
        # Given: Point 생성 후, is_active False 로 전환
        user_point1 = self._give_user_points(self.user, 100)
        user_point1.is_active = False
        user_point1.save()

        # When:
        total_point = get_user_available_total_point(self.user.id)

        # Then: 0 반환
        self.assertEqual(total_point, 0)

    def test_use_point_should_raise_error_when_user_has_not_enough_point(self):
        # Given:
        # Expect:
        with self.assertRaises(NotEnoughUserPoints):
            use_point(self.user.id, 100, 'test')

    def test_use_point_should_success_when_user_has_enough_point(self):
        # Given: 유저에게 포인트 지급
        self._give_user_points(self.user, 100)
        # And: 100 받음
        self.assertEqual(get_user_available_total_point(self.user.id), 100)

        # When:
        user_point = use_point(self.user.id, 100, 'test')

        # Then: 100 을 사용하여 0 원 남았습니다.
        self.assertEqual(get_user_available_total_point(self.user.id), 0)
        # And: -100
        self.assertEqual(UserPoint.objects.get(id=user_point.id).point, -100)
