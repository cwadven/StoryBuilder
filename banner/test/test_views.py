import json
from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse

from banner.models import BannerType, Banner
from config.test_helper.helper import LoginMixin


class BannerListAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(BannerListAPIViewTestCase, self).setUp()
        self.login()
        self.banner_type = BannerType.objects.create(name='Test Banner Type', description='Test Description')
        self.banner1 = Banner.objects.create(
            title='Banner 1',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=1,
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
            sequence=2,
            start_time=datetime.now() - timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1),
            is_active=True,
        )

    def test_banner_list_api(self):
        # Given:
        # When:
        response = self.c.get(reverse('banner:banner_list'))
        content = json.loads(response.content)

        # Then: 정상 접근
        self.assertEqual(response.status_code, 200)
        # And: story list 반환
        self.assertEqual(len(content['banners']), 2)
        # And: order by sequence 역정렬 순
        self.assertEqual(content['banners'][0]['id'], self.banner2.id)
        self.assertEqual(content['banners'][0]['banner_type_name'], self.banner2.banner_type.name)
        self.assertEqual(content['banners'][1]['id'], self.banner1.id)
        self.assertEqual(content['banners'][1]['banner_type_name'], self.banner1.banner_type.name)
