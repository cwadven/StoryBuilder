from datetime import datetime, timedelta

from django.test import TestCase

from banner.dtos import BannerListItemDTO, BannerDetailItemDTO
from banner.models import BannerType, Banner


class BannerListItemDTOTestCase(TestCase):
    def setUp(self):
        self.banner_type = BannerType.objects.create(name='Test Banner Type', description='Test Description')
        self.banner = Banner.objects.create(
            title='Active Banner (no end time)',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=1,
            start_time=datetime.now() - timedelta(days=1),
            is_active=True,
        )

    def test_banner_list_item_dto(self):
        # Given:
        # When: dto 객체 생성
        banner_list_item_dto = BannerListItemDTO.of(self.banner)
        banner_list_item = banner_list_item_dto.to_dict()

        # Then: set dto
        self.assertEqual(banner_list_item['id'], self.banner.id)
        self.assertEqual(banner_list_item['title'], self.banner.title)
        self.assertEqual(banner_list_item['background_image'], self.banner.background_image)
        self.assertEqual(banner_list_item['background_color'], self.banner.background_color)
        self.assertEqual(banner_list_item['banner_type_name'], self.banner.banner_type.name)


class BannerDetailItemDTOTestCase(TestCase):
    def setUp(self):
        self.banner_type = BannerType.objects.create(name='Test Banner Type', description='Test Description')
        self.banner = Banner.objects.create(
            title='Active Banner (no end time)',
            description='Test Description',
            background_image='https://example.com/banner-image.jpg',
            background_color='#000000',
            banner_type=self.banner_type,
            sequence=1,
            start_time=datetime.now() - timedelta(days=1),
            is_active=True,
        )

    def test_banner_detail_item_dto(self):
        # Given:
        # When: dto 객체 생성
        banner_detail_item_dto = BannerDetailItemDTO.of(self.banner)
        banner_detail_item = banner_detail_item_dto.to_dict()

        # Then: set dto
        self.assertEqual(banner_detail_item['id'], self.banner.id)
        self.assertEqual(banner_detail_item['title'], self.banner.title)
        self.assertEqual(banner_detail_item['description'], self.banner.description)
        self.assertEqual(banner_detail_item['background_image'], self.banner.background_image)
        self.assertEqual(banner_detail_item['background_color'], self.banner.background_color)
        self.assertEqual(banner_detail_item['banner_type_name'], self.banner.banner_type.name)
        self.assertEqual(banner_detail_item['created_at'], self.banner.created_at.strftime('%Y-%m-%d %H:%M:%S'))
