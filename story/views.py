from rest_framework.response import Response
from rest_framework.views import APIView

from common_decorator import mandatories
from story.dtos import PlayingSheetDTO
from story.models import SheetAnswer, UserStorySolve
from story.services import (
    get_running_start_sheet_by_story,
    get_sheet_answer_with_next_path_responses,
    get_valid_answer_info_with_random_quantity,
)


class StoryPlayAPIView(APIView):
    def get(self, request, story_id):
        start_sheet = get_running_start_sheet_by_story(story_id)

        if request.user.is_authenticated:
            UserStorySolve.objects.get_or_create(
                story_id=story_id,
                user=request.user,
            )

        playing_sheet = PlayingSheetDTO.of(start_sheet).to_dict()
        return Response(playing_sheet, status=200)


class SheetAnswerCheckAPIView(APIView):
    @mandatories('sheet_id', 'answer')
    def post(self, request, m):
        sheet_id = m['sheet_id']
        answer_responses = get_sheet_answer_with_next_path_responses(sheet_id)

        is_valid, sheet_answer_id, next_sheet_id = get_valid_answer_info_with_random_quantity(
            answer=m['answer'],
            answer_responses=answer_responses
        )

        try:
            sheet_answer = SheetAnswer.objects.get(id=sheet_answer_id)
            answer_reply = sheet_answer.answer_reply
        except SheetAnswer.DoesNotExist:
            return Response({'is_valid': is_valid, 'next_sheet_id': next_sheet_id, 'answer_reply': None}, status=200)

        return Response({'is_valid': is_valid, 'next_sheet_id': next_sheet_id, 'answer_reply': answer_reply}, status=200)
