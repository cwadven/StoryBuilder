from rest_framework.response import Response
from rest_framework.views import APIView

from common_decorator import mandatories, custom_login_required_for_method
from story.dtos import PlayingSheetDTO
from story.models import SheetAnswer, UserStorySolve, UserSheetAnswerSolve, NextSheetPath
from story.services import (
    get_running_start_sheet_by_story,
    get_sheet_answer_with_next_path_responses,
    get_valid_answer_info_with_random_quantity,
    get_running_sheet,
    validate_user_playing_sheet,
)


class StoryPlayAPIView(APIView):
    @custom_login_required_for_method
    def get(self, request, story_id):
        start_sheet = get_running_start_sheet_by_story(story_id)

        UserStorySolve.objects.get_or_create(
            story_id=story_id,
            user=request.user,
        )
        UserSheetAnswerSolve.generate_cls_if_first_time(
            user=request.user,
            sheet_id=start_sheet.id,
        )

        playing_sheet = PlayingSheetDTO.of(start_sheet).to_dict()
        return Response(playing_sheet, status=200)


class SheetPlayAPIView(APIView):
    @custom_login_required_for_method
    def get(self, request, sheet_id):
        validate_user_playing_sheet(request.user.id, sheet_id)

        sheet = get_running_sheet(sheet_id)
        UserSheetAnswerSolve.generate_cls_if_first_time(
            user=request.user,
            sheet_id=sheet.id,
        )

        playing_sheet = PlayingSheetDTO.of(sheet).to_dict()
        return Response(playing_sheet, status=200)


class SheetAnswerCheckAPIView(APIView):
    @mandatories('sheet_id', 'answer')
    @custom_login_required_for_method
    def post(self, request, m):
        # 로그인 테스트케이스 추가
        sheet_id = m['sheet_id']
        answer_responses = get_sheet_answer_with_next_path_responses(sheet_id)
        answer_reply = None

        is_valid, sheet_answer_id, next_sheet_path_id, next_sheet_id = get_valid_answer_info_with_random_quantity(
            answer=m['answer'],
            answer_responses=answer_responses
        )

        try:
            sheet_answer = SheetAnswer.objects.select_related(
                'sheet'
            ).get(
                id=sheet_answer_id
            )
            answer_reply = sheet_answer.answer_reply
            if is_valid and request.user.is_authenticated:
                user_sheet_answer_solve = UserSheetAnswerSolve.objects.get(
                    user=request.user,
                    sheet=sheet_answer.sheet,
                )
                try:
                    next_sheet_path = NextSheetPath.objects.get(
                        id=next_sheet_path_id,
                        sheet_id=next_sheet_id,
                    )
                except NextSheetPath.DoesNotExist:
                    next_sheet_path = None
                user_sheet_answer_solve.solved_sheet_action(
                    answer=sheet_answer.answer,
                    sheet_question=sheet_answer.sheet.question,
                    solved_sheet_version=sheet_answer.sheet.version,
                    solved_answer_version=sheet_answer.version,
                    next_sheet_path=next_sheet_path,
                )
        except SheetAnswer.DoesNotExist:
            return Response({'is_valid': is_valid, 'next_sheet_id': next_sheet_id, 'answer_reply': answer_reply}, status=200)

        return Response({'is_valid': is_valid, 'next_sheet_id': next_sheet_id, 'answer_reply': answer_reply}, status=200)
