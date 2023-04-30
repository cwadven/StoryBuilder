from datetime import datetime, timedelta

from django.test import TestCase

from banner.models import BannerType, Banner
from banner.services import get_active_banners, get_active_banner
from config.common.exception_codes import BannerDoesNotExists


class GetActiveBannersTestCase(TestCase):
    def setUp(self):
        self.banner_type = BannerType.objects.create(name='Test Banner Type', description='Test Description')
        self.banner1 = Banner.objects.create(
            title='Banner 1',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=2,
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1),
            is_active=True,
        )
        self.banner2 = Banner.objects.create(
            title='Banner 2',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=1,
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1),
            is_active=True,
        )

    def test_get_active_banners(self):
        # Given: Test default behavior (order_by -id)
        now = datetime.now()
        active_banners = get_active_banners(now=now, order_by=['-id'])
        # Expected: id 순으로 생성
        self.assertEqual(list(active_banners), [self.banner2, self.banner1])

        # Given: Test default behavior (order_by -sequence)
        active_banners = get_active_banners(now=now, order_by=['-sequence'])
        # Expected: sequence 역정렬 순으로 생성
        self.assertEqual(list(active_banners), [self.banner1, self.banner2])

    def test_get_active_banner_should_return_banner(self):
        # Given:
        now = datetime.now()

        # When:
        active_banner = get_active_banner(banner_id=self.banner1.id, now=now)

        # Then: banner1 반환
        self.assertEqual(active_banner.id, self.banner1.id)

    def test_get_active_banner_should_raise_error_when_banner_not_exists(self):
        # Given: banner1 비 활성화
        self.banner1.is_active = False
        self.banner1.save()

        # Expected: BannerDoesNotExists 에러 반환
        with self.assertRaises(BannerDoesNotExists):
            get_active_banner(banner_id=self.banner1.id)
