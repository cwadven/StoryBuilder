from django.test import TestCase

from account.models import User
from story.dtos import PlayingSheetDTO
from story.models import Sheet, Story


class DTOTopicItemTestCase(TestCase):
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

    def test_playing_sheet_dto(self):
        # Given:
        # When: dto 객체 생성
        playing_sheet_dto = PlayingSheetDTO.of(self.start_sheet)
        playing_sheet = playing_sheet_dto.to_dict()

        # Then: set dto
        self.assertEqual(playing_sheet.get('id'), self.start_sheet.id)
        self.assertEqual(playing_sheet.get('title'), self.start_sheet.title)
        self.assertEqual(playing_sheet.get('question'), self.start_sheet.question)
        self.assertEqual(playing_sheet.get('image'), self.start_sheet.image)
        self.assertEqual(playing_sheet.get('background_image'), self.start_sheet.background_image)
