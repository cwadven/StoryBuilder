from rest_framework.response import Response
from rest_framework.views import APIView

from common_decorator import mandatories, custom_login_required_for_method
from story.constants import StoryErrorMessage
from story.dtos import PlayingSheetInfoDTO, PreviousSheetInfoDTO
from story.models import SheetAnswer, UserStorySolve, UserSheetAnswerSolve, NextSheetPath, StoryLike, Story
from story.services import (
    get_running_start_sheet_by_story,
    get_sheet_answer_with_next_path_responses,
    get_valid_answer_info_with_random_quantity,
    get_running_sheet,
    validate_user_playing_sheet, get_sheet_solved_user_sheet_answer, get_recent_played_sheet_by_story_id,
    create_story_like, delete_story_like,
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

        solved_user_sheet_answer = get_sheet_solved_user_sheet_answer(request.user.id, start_sheet.id)
        if solved_user_sheet_answer:
            return Response(
                data=PlayingSheetInfoDTO.of(
                    start_sheet,
                    solved_user_sheet_answer
                ).to_dict(),
                status=200
            )

        playing_sheet = PlayingSheetInfoDTO.of(start_sheet).to_dict()
        return Response(playing_sheet, status=200)


class StoryPlayGetRecentUnsolvedSheetAPIView(APIView):
    @custom_login_required_for_method
    def get(self, request, story_id):
        start_sheet = get_running_start_sheet_by_story(story_id)

        solved_user_sheet_answer = get_sheet_solved_user_sheet_answer(request.user.id, start_sheet.id)
        if solved_user_sheet_answer:
            recent_sheet = get_recent_played_sheet_by_story_id(
                user_id=request.user.id,
                story_id=story_id,
            )
            return Response(
                data={'recent_sheet_id': recent_sheet.id},
                status=200
            )

        return Response(data={'message': '최근에 해결 못한 sheet 가 없습니다.'}, status=400)


class SheetPlayAPIView(APIView):
    @custom_login_required_for_method
    def get(self, request, sheet_id):
        validate_user_playing_sheet(request.user.id, sheet_id)

        sheet = get_running_sheet(sheet_id)
        user_sheet_answer_solve, _ = UserSheetAnswerSolve.generate_cls_if_first_time(
            user=request.user,
            sheet_id=sheet.id,
        )

        solved_user_sheet_answer = get_sheet_solved_user_sheet_answer(request.user.id, sheet_id)
        previous_sheet_infos = UserSheetAnswerSolve.get_previous_user_sheet_answer_solves_with_current_sheet_id(
            user_id=request.user.id,
            current_sheet_id=sheet_id,
        )
        previous_sheet_info_dto_list = list(
            map(
                lambda previous_sheet_info: PreviousSheetInfoDTO(
                    sheet_id=previous_sheet_info['sheet_id'],
                    title=previous_sheet_info['sheet__title'],
                ),
                previous_sheet_infos
            )
        )
        if solved_user_sheet_answer:
            return Response(
                data=PlayingSheetInfoDTO.of(
                    sheet=sheet,
                    user_sheet_answer_solve=solved_user_sheet_answer,
                    previous_sheet_infos=previous_sheet_info_dto_list,
                ).to_dict(),
                status=200
            )

        playing_sheet = PlayingSheetInfoDTO.of(
            sheet=sheet,
            previous_sheet_infos=previous_sheet_info_dto_list,
        ).to_dict()
        return Response(playing_sheet, status=200)


class SheetAnswerCheckAPIView(APIView):
    @mandatories('sheet_id', 'answer')
    @custom_login_required_for_method
    def post(self, request, m):
        sheet_id = m['sheet_id']
        answer_responses = get_sheet_answer_with_next_path_responses(sheet_id)
        answer_reply = None

        solved_user_sheet_answer = get_sheet_solved_user_sheet_answer(request.user.id, sheet_id)
        if solved_user_sheet_answer:
            return Response({'message': StoryErrorMessage.ALREADY_SOLVED.label}, status=400)

        is_valid, sheet_answer_id, next_sheet_path_id, next_sheet_id = get_valid_answer_info_with_random_quantity(
            answer=m['answer'],
            answer_responses=answer_responses
        )

        # 나중에 Service 레이어로 위치 변환
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
                    solved_sheet_answer=sheet_answer,
                    next_sheet_path=next_sheet_path,
                )
        except (SheetAnswer.DoesNotExist, UserSheetAnswerSolve.DoesNotExist):
            return Response({'is_valid': is_valid, 'next_sheet_id': next_sheet_id, 'answer_reply': answer_reply}, status=200)

        return Response({'is_valid': is_valid, 'next_sheet_id': next_sheet_id, 'answer_reply': answer_reply}, status=200)


class StoryLikeAPIView(APIView):
    @custom_login_required_for_method
    def post(self, request, story_id):
        try:
            create_story_like(story_id, request.user.id)
        except Story.DoesNotExist:
            return Response({'message': 'story에 문제가 있습니다.'}, status=400)

        return Response(status=200)

    @custom_login_required_for_method
    def delete(self, request, story_id):
        try:
            delete_story_like(story_id, request.user.id)
        except StoryLike.DoesNotExist:
            return Response({'message': '좋아요를 한적이 없습니다.'}, status=400)

        return Response(status=200)
