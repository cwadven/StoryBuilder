from django.test import TestCase

from account.models import User
from hint.dtos import UserSheetHintInfoDTO, UserSheetHintInfosResponse
from hint.models import SheetHint
from story.models import Sheet, Story


class DTOUserSheetHintInfoTestCase(TestCase):
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
        self.start_sheet_hint = SheetHint.objects.create(
            sheet=self.start_sheet,
            hint='test_hint',
            image='test_image',
            sequence=1,
            point=10,
        )

    def test_user_sheet_hint_info_dto_when_user_has_history(self):
        # Given:
        # When: dto 객체 생성
        user_sheet_hint_info_dto = UserSheetHintInfoDTO.of(self.start_sheet_hint, True)
        user_sheet_hint_info = user_sheet_hint_info_dto.to_dict()

        # Then: set dto
        self.assertEqual(user_sheet_hint_info.get('id'), self.start_sheet_hint.id)
        self.assertEqual(user_sheet_hint_info.get('hint'), self.start_sheet_hint.hint)
        self.assertEqual(user_sheet_hint_info.get('point'), self.start_sheet_hint.point)
        self.assertEqual(user_sheet_hint_info.get('image'), self.start_sheet_hint.image)
        self.assertTrue(user_sheet_hint_info.get('has_history'))

    def test_user_sheet_hint_info_dto_when_user_not_have_history(self):
        # Given:
        # When: dto 객체 생성
        user_sheet_hint_info_dto = UserSheetHintInfoDTO.of(self.start_sheet_hint, False)
        user_sheet_hint_info = user_sheet_hint_info_dto.to_dict()

        # Then: set dto
        self.assertEqual(user_sheet_hint_info.get('id'), self.start_sheet_hint.id)
        self.assertEqual(user_sheet_hint_info.get('hint'), '')
        self.assertEqual(user_sheet_hint_info.get('point'), self.start_sheet_hint.point)
        self.assertEqual(user_sheet_hint_info.get('image'), '')
        self.assertFalse(user_sheet_hint_info.get('has_history'))


class DTOUserSheetHintInfosResponseTestCase(TestCase):
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
        self.start_sheet_hint = SheetHint.objects.create(
            sheet=self.start_sheet,
            hint='test_hint',
            image='test_image',
            sequence=1,
            point=10,
        )

    def test_user_sheet_hint_infos_response(self):
        # Given:
        # When: dto 객체 생성
        user_sheet_hint_infos_response = UserSheetHintInfosResponse([])
        user_sheet_hint_infos_response_dict = user_sheet_hint_infos_response.to_dict()

        # Then: set dto
        self.assertEqual(user_sheet_hint_infos_response_dict.get('user_sheet_hint_infos'), [])
