from datetime import datetime, timedelta

from django.test import TestCase

from banner.models import BannerType, Banner


class BannerManagerTestCase(TestCase):
    def setUp(self):
        self.banner_type = BannerType.objects.create(name='Test Banner Type', description='Test Description')
        self.banner = Banner.objects.create(
            title='Test Banner',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=1,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=1),
            is_active=True,
        )

    def test_banner_manager_get_activate(self):
        # Given: Banner is active created
        now = datetime.now()
        activate_banners = Banner.objects.get_activate(now=now)
        # Expected:
        self.assertIn(self.banner, activate_banners)

        # Given: Banner is not active
        inactive_banner = Banner.objects.create(
            title='Inactive Banner',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=2,
            start_time=datetime.now(),
            end_time=datetime.now() - timedelta(days=1),
            is_active=False,
        )
        # Expected:
        activate_banners = Banner.objects.get_activate(now=now)
        self.assertNotIn(inactive_banner, activate_banners)
