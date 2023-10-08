from django.test import TestCase

from account.models import User
from story.cmd_dtos import CMSStorySheetMapItemDTO
from story.models import (
    Sheet,
    Story,
)


class CMSStorySheetMapItemDTOTest(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=True,
            is_final=False,
        )

    def test_of_method(self):
        # Given:
        hint_count = 2
        answer_ids = [101, 102, 103, 104]
        # And:
        expected_data = {
            'id': self.sheet.id,
            'title': self.sheet.title,
            'question': self.sheet.question,
            'image': self.sheet.image,
            'background_image': self.sheet.background_image,
            'hint_count': hint_count,
            'answer_ids': answer_ids,
        }

        # When: 동작 실행
        dto = CMSStorySheetMapItemDTO.of(self.sheet, hint_count, answer_ids).to_dict()

        # Then: 결과 확인
        self.assertDictEqual(dto, expected_data)