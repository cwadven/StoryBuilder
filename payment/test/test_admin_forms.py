from io import BytesIO
from PIL import Image
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase

from account.models import User
from payment.admin_forms import PointProductAdminForm
from payment.models import PointProduct


class TestPointProductAdminForm(TestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(
            username='superuser', password='secret', email='admin@example.com'
        )
        self.client.login(username='superuser', password='secret')
        self.form_data = {
            'author': self.super_user.id,
            'title': 'test2',
            'description': 'test2',
            'image': '',
            'point': 1000,
            'is_active': True,
            'start_time': '2022-01-10',
            'end_time': '2022-01-10',
            'quantity': 10,
            'is_sold_out': False,
            'review_rate': 0,
            'bought_count': 0,
            'review_count': 0,
            'price': 1000,
            '_save': 'Save',
        }
        im = Image.new(mode='RGB', size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, 'JPEG')
        im_io.seek(0)
        self.image = InMemoryUploadedFile(
            im_io, None, 'random-name.jpg', 'image/jpeg', len(im_io.getvalue()), None
        )

    @patch('payment.admin_forms.upload_file_to_presigned_url', Mock())
    @patch('payment.admin_forms.generate_presigned_url')
    def test_point_product_admin_form_success(self, mock_generate_presigned_url):
        # Given: 파일을 생성합니다.
        mock_generate_presigned_url.return_value = {
            'url': 'test',
            'fields': {
                'key': 'test'
            },
        }
        file_form_data = {
            'image_file': self.image,
        }

        # When: form 에 요청했을 경우
        form = PointProductAdminForm(self.form_data, file_form_data)

        # Then: 정상적으로 데이터 생성가능 하도록 True
        self.assertTrue(form.is_valid())
        instance = form.save()

        point_product = PointProduct.objects.get(id=instance.id)
        self.assertEqual(point_product.title, self.form_data['title'])
        self.assertEqual(point_product.description, self.form_data['description'])
        self.assertEqual(point_product.image, 'testtest')
