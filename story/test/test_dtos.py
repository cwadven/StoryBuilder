from django.test import TestCase

from account.models import User
from story.dtos import PlayingSheetDTO, SheetAnswerResponseDTO, PlayingSheetAnswerSolvedDTO
from story.models import Sheet, Story, SheetAnswer, NextSheetPath, UserSheetAnswerSolve


class DTOPlayingSheetTestCase(TestCase):
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
        self.assertEqual(playing_sheet.get('sheet_id'), self.start_sheet.id)
        self.assertEqual(playing_sheet.get('title'), self.start_sheet.title)
        self.assertEqual(playing_sheet.get('question'), self.start_sheet.question)
        self.assertEqual(playing_sheet.get('image'), self.start_sheet.image)
        self.assertEqual(playing_sheet.get('background_image'), self.start_sheet.background_image)


class DTOSheetAnswerResponseTestCase(TestCase):
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
        self.final_sheet1 = Sheet.objects.create(
            story=self.story,
            title='test_title1',
            question='test_question1',
            image='https://image.test',
            background_image='https://image.test',
            is_start=False,
            is_final=True,
        )
        self.next_sheet_path = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet1,
            quantity=10,
        )

    def test_sheet_answer_response_dto(self):
        # Given: SheetAnswerResponseDTO 에 맞는 타입 생성
        start_sheet_values = self.start_sheet.sheetanswer_set.all().values(
            'id',
            'answer',
            'answer_reply',
            'nextsheetpath',
            'next_sheet_paths__nextsheetpath__sheet_id',
            'next_sheet_paths__nextsheetpath__quantity',
        )

        # When: dto 객체 생성
        sheet_answer_response_dto = SheetAnswerResponseDTO.of(start_sheet_values[0])
        sheet_answer_response = sheet_answer_response_dto.to_dict()

        # Then: set dto
        self.assertEqual(sheet_answer_response.get('id'), start_sheet_values[0]['id'])
        self.assertEqual(sheet_answer_response.get('answer'), start_sheet_values[0]['answer'])
        self.assertEqual(sheet_answer_response.get('answer_reply'), start_sheet_values[0]['answer_reply'])
        self.assertEqual(sheet_answer_response.get('next_sheet_path_id'), start_sheet_values[0]['nextsheetpath'])
        self.assertEqual(sheet_answer_response.get('next_sheet_id'), start_sheet_values[0]['next_sheet_paths__nextsheetpath__sheet_id'])
        self.assertEqual(sheet_answer_response.get('next_sheet_quantity'), start_sheet_values[0]['next_sheet_paths__nextsheetpath__quantity'])


class DTOPlayingSheetAnswerSolvedDTOTestCase(TestCase):
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
        self.final_sheet1 = Sheet.objects.create(
            story=self.story,
            title='test_title1',
            question='test_question1',
            image='https://image.test',
            background_image='https://image.test',
            is_start=False,
            is_final=True,
        )
        self.next_sheet_path = NextSheetPath.objects.create(
            answer=self.start_sheet_answer1,
            sheet=self.final_sheet1,
            quantity=10,
        )
        self.user_sheet_answer_solve = UserSheetAnswerSolve.objects.create(
            user=self.user,
            story=self.story,
            sheet=self.start_sheet,
            solved_sheet_version=1,
            solved_answer_version=1,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[0][0],
            next_sheet_path=self.next_sheet_path,
            answer=self.start_sheet_answer1,
        )

    def test_playing_sheet_answer_solved_dto(self):
        # Given:
        # When: dto 객체 생성
        playing_sheet_answer_solved_dto = PlayingSheetAnswerSolvedDTO.of(self.user_sheet_answer_solve)
        playing_sheet_answer_solved = playing_sheet_answer_solved_dto.to_dict()

        # Then: set dto
        self.assertEqual(playing_sheet_answer_solved.get('next_sheet_id'), self.final_sheet1.id)
        self.assertEqual(playing_sheet_answer_solved.get('answer_reply'), self.start_sheet_answer1.answer_reply)
        self.assertTrue(playing_sheet_answer_solved.get('is_solved'))
