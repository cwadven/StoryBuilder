from io import BytesIO
from PIL import Image
from unittest.mock import Mock, patch

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase

from account.models import User
from story.admin_forms import StoryAdminForm, SheetAdminForm
from story.models import Story, Sheet


class TestStoryAdminForm(TestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(
            username='superuser', password='secret', email='admin@example.com'
        )
        self.client.login(username='superuser', password='secret')
        self.story = Story.objects.create(
            author=self.super_user,
            title='test_story',
            description='test_description',
        )
        self.form_data = {
            'author': self.super_user.id,
            'title': 'test2',
            'description': 'test2',
            'image': '',
            'background_image': '',
            'played_count': 0,
            'view_count': 0,
            'review_rate': 0,
            'like_count': 0,
            'playing_point': 0,
            'free_to_play_sheet_count': 0,
            'level': 0,
            '_save': 'Save',
        }
        im = Image.new(mode='RGB', size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, 'JPEG')
        im_io.seek(0)
        self.image = InMemoryUploadedFile(
            im_io, None, 'random-name.jpg', 'image/jpeg', len(im_io.getvalue()), None
        )

    @patch('story.admin_forms.upload_file_to_presigned_url', Mock())
    @patch('story.admin_forms.generate_presigned_url')
    def test_story_admin_form_success(self, mock_generate_presigned_url):
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
        form = StoryAdminForm(self.form_data, file_form_data)

        # Then: 정상적으로 데이터 생성가능 하도록 True
        form.is_valid()
        self.assertTrue(form.is_valid())
        instance = form.save()

        story = Story.objects.get(id=instance.id)
        self.assertEqual(story.title, self.form_data['title'])
        self.assertEqual(story.description, self.form_data['description'])
        self.assertEqual(story.image, 'testtest')
        self.assertEqual(story.background_image, 'testtest')


class TestSheetAdminForm(TestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(
            username='superuser', password='secret', email='admin@example.com'
        )
        self.client.login(username='superuser', password='secret')
        self.story = Story.objects.create(
            author=self.super_user,
            title='test_story',
            description='test_description',
        )
        self.start_sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            is_start=True,
            is_final=False,
        )
        self.form_data = {
            'story': self.story.id,
            'title': 'test2',
            'question': 'test2',
            'image': '',
            'background_image': '',
            'version': 0,
            'is_start': True,
            '_save': 'Save',
        }
        im = Image.new(mode='RGB', size=(200, 200))
        im_io = BytesIO()
        im.save(im_io, 'JPEG')
        im_io.seek(0)
        self.image = InMemoryUploadedFile(
            im_io, None, 'random-name.jpg', 'image/jpeg', len(im_io.getvalue()), None
        )

    @patch('story.admin_forms.upload_file_to_presigned_url', Mock())
    @patch('story.admin_forms.generate_presigned_url')
    def test_sheet_admin_form_success(self, mock_generate_presigned_url):
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
        form = SheetAdminForm(self.form_data, file_form_data)

        # Then: 정상적으로 데이터 생성가능 하도록 True
        self.assertTrue(form.is_valid())
        instance = form.save()

        sheet = Sheet.objects.get(id=instance.id)
        self.assertEqual(sheet.title, self.form_data['title'])
        self.assertEqual(sheet.question, self.form_data['question'])
        self.assertEqual(sheet.image, 'testtest')
        self.assertEqual(sheet.background_image, 'testtest')
