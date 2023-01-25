from django.test import TestCase

from account.models import User
from point.dtos import UserPointInfoResponseDTO
from story.models import Sheet, Story


class DTOUserPointInfoResponseTestCase(TestCase):
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

    def test_user_point_info_response_dto(self):
        # Given:
        total_point = 30

        # When: dto 객체 생성
        user_point_info_response_dto = UserPointInfoResponseDTO(
            total_point=total_point
        )
        user_point_info_response = user_point_info_response_dto.to_dict()

        # Then: set dto
        self.assertEqual(user_point_info_response['total_point'], total_point)
