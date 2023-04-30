from datetime import datetime
from io import BytesIO
from PIL import Image
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase

from account.models import User
from banner.admin_forms import BannerAdminForm
from banner.models import Banner, BannerType


class TestBannerAdminForm(TestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(
            username='superuser', password='secret', email='admin@example.com'
        )
        self.client.login(username='superuser', password='secret')
        self.banner_type = BannerType.objects.create(name='Test Banner Type', description='Test Description')
        self.form_data = {
            'author': self.super_user.id,
            'title': 'test2',
            'description': 'test2',
            'background_image': '',
            'background_color': '',
            'banner_type': self.banner_type.id,
            'sequence': 1,
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'is_active': True,
            '_save': 'Save',
        }
        im = Image.new(mode='RGB', size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, 'JPEG')
        im_io.seek(0)
        self.image = InMemoryUploadedFile(
            im_io, None, 'random-name.jpg', 'image/jpeg', len(im_io.getvalue()), None
        )

    @patch('banner.admin_forms.upload_file_to_presigned_url', Mock())
    @patch('banner.admin_forms.generate_presigned_url')
    def test_banner_admin_form_success(self, mock_generate_presigned_url):
        # Given: 파일을 생성합니다.
        mock_generate_presigned_url.return_value = {
            'url': 'test',
            'fields': {
                'key': 'test'
            },
        }
        file_form_data = {
            'image_file': self.image,
            'background_image_file': self.image,
        }

        # When: form 에 요청했을 경우
        form = BannerAdminForm(self.form_data, file_form_data)

        # Then: 정상적으로 데이터 생성가능 하도록 True
        form.is_valid()
        self.assertTrue(form.is_valid())
        instance = form.save()

        banner = Banner.objects.get(id=instance.id)
        self.assertEqual(banner.title, self.form_data['title'])
        self.assertEqual(banner.description, self.form_data['description'])
        self.assertEqual(banner.background_image, 'testtest')
        self.assertEqual(banner.banner_type_id, self.banner_type.id)
