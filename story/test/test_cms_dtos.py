from django.test import TestCase

from account.models import User
from story.cmd_dtos import (
    CMSStorySheetMapItemDTO,
    CMSStorySheetAnswerMapItemDTO,
    CMSStoryAnswerNextPathItemDTO,
    CMSStoryAnswerNextPathMapItemDTO
)
from story.models import (
    Sheet,
    SheetAnswer,
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


class CMSStorySheetAnswerMapItemDTOTest(TestCase):
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
        self.sheet_answer1 = SheetAnswer.objects.create(
            sheet=self.sheet,
            answer='test',
            answer_reply='test_reply',
        )

    def test_of_method(self):
        # Given:
        expected_data = {
            'id': self.sheet_answer1.id,
            'sheet_id': self.sheet_answer1.sheet_id,
            'answer': self.sheet_answer1.answer,
            'answer_reply': self.sheet_answer1.answer_reply,
            'is_always_correct': self.sheet_answer1.is_always_correct,
        }

        # When: 동작 실행
        dto = CMSStorySheetAnswerMapItemDTO.of(self.sheet_answer1).to_dict()

        # Then: 결과 확인
        self.assertDictEqual(dto, expected_data)


class CMSStoryAnswerNextPathMapResponseTest(TestCase):
    def setUp(self):
        self.user = User.objects.all()[0]
        self.story = Story.objects.create(
            author=self.user,
            title='test_story',
            description='test_description',
            image='https://image.test',
            background_image='https://image.test',
        )
        self.start_sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=True,
            is_final=False,
        )
        self.start_sheet_answer1 = SheetAnswer.objects.create(
            sheet=self.start_sheet,
            answer='test',
            answer_reply='test_reply',
        )
        self.next_paths = [CMSStoryAnswerNextPathItemDTO(sheet_id=self.start_sheet_answer1.id, quantity=4)]

    def test_of_method(self):
        # Given:
        # When:
        answer_next_path = CMSStoryAnswerNextPathMapItemDTO.of(self.start_sheet_answer1, self.next_paths)

        # Then:
        self.assertEqual(answer_next_path.answer_id, self.start_sheet_answer1.id)
        self.assertEqual(answer_next_path.next_paths[0].sheet_id, self.start_sheet_answer1.id)
        self.assertEqual(answer_next_path.next_paths[0].quantity, 4)
