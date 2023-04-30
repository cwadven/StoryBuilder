from datetime import datetime, timedelta

from django.test import TestCase

from banner.models import BannerType, Banner


class BannerTestCase(TestCase):
    def setUp(self):
        self.banner_type = BannerType.objects.create(name='Test Banner Type', description='Test Description')

    def test_banner_status_property(self):
        # Given: Test active banner (no end time)
        active_banner_no_end_time = Banner.objects.create(
            title='Active Banner (no end time)',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=1,
            start_time=datetime.now() - timedelta(days=1),
            is_active=True,
        )
        # Expected:
        self.assertEqual(active_banner_no_end_time.status, '활성')

        # Given: Test active banner (with end time)
        active_banner_with_end_time = Banner.objects.create(
            title='Active Banner (with end time)',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=2,
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1),
            is_active=True,
        )
        # Expected:
        self.assertEqual(active_banner_with_end_time.status, '활성')

        # Given: Test inactive banner (is_active True)
        inactive_banner = Banner.objects.create(
            title='Inactive Banner',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=3,
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() - timedelta(days=1),
            is_active=True,
        )
        # Expected:
        self.assertEqual(inactive_banner.status, '비활성')

        # Given: Test inactive banner (is_active false)
        inactive_banner = Banner.objects.create(
            title='Inactive Banner',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=3,
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() - timedelta(days=1),
            is_active=False,
        )
        # Expected:
        self.assertEqual(inactive_banner.status, '비활성')
