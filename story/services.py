import random
from typing import List, Optional

from django.db import transaction
from django.db.models import Q

from common_library import get_max_int_from_queryset
from config.common.exception_codes import StartingSheetDoesNotExists, SheetDoesNotExists, SheetNotAccessibleException, \
    StoryDoesNotExists
from story.constants import DEFAULT_POPULAR_KILL_SWITCH_STORY_COUNT
from story.dtos import SheetAnswerResponseDTO, UserSheetAnswerSolveHistoryItemDTO
from story.models import Sheet, UserSheetAnswerSolve, StoryEmailSubscription, StoryLike, Story, PopularStory, \
    StorySlackSubscription, UserSheetAnswerSolveHistory, WrongAnswer


def get_active_stories(search='', start_row=None, end_row=None, user=None) -> List[Story]:
    qs = Story.objects.get_actives(user).order_by('-id')

    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

    if start_row is not None and end_row is not None:
        return list(qs[start_row:end_row])
    return list(qs)


def get_active_popular_stories(user=None) -> List[PopularStory]:
    qs = PopularStory.objects.get_actives(user).order_by('rank')
    return list(qs)


def get_stories_order_by_fields(user=None, *args) -> List[Story]:
    qs = Story.objects.get_actives(user).filter(like_count__gt=0).order_by(*args)
    return list(qs[:DEFAULT_POPULAR_KILL_SWITCH_STORY_COUNT])


def get_active_story_by_id(story_id: int, user=None) -> Story:
    try:
        return Story.objects.get_actives(user=user).get(
            id=story_id,
        )
    except Story.DoesNotExist:
        raise StoryDoesNotExists()


def get_running_start_sheet_by_story(story_id) -> Sheet:
    """
    Story 에서 시작하는 처음 Sheet 가져오기
    """
    try:
        return Sheet.objects.get(
            story_id=story_id,
            story__is_deleted=False,
            story__displayable=True,
            is_start=True,
            is_deleted=False
        )
    except Sheet.DoesNotExist:
        raise StartingSheetDoesNotExists()


def get_running_sheet(sheet_id) -> Sheet:
    try:
        return Sheet.objects.get(
            id=sheet_id,
            story__is_deleted=False,
            story__displayable=True,
            is_deleted=False
        )
    except Sheet.DoesNotExist:
        raise SheetDoesNotExists()


def validate_user_playing_sheet(user_id: int, sheet_id: int):
    """
    check UserSheetAnswerSolve next_sheet_path of sheet exists
    And check if answer has been changed

    And check if sheet is start then just return
    """
    try:
        if Sheet.objects.get(id=sheet_id).is_start:
            return
        user_sheet_answer_solve = UserSheetAnswerSolve.objects.select_related(
            'next_sheet_path',
            'sheet',
        ).get(
            user_id=user_id,
            next_sheet_path__sheet_id=sheet_id,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
        )
    except (UserSheetAnswerSolve.DoesNotExist, Sheet.DoesNotExist):
        raise SheetNotAccessibleException()

    if not (user_sheet_answer_solve.answer in get_sheet_answers(user_sheet_answer_solve.sheet_id)):
        raise SheetNotAccessibleException()


def get_sheet_answers(sheet_id: int) -> set:
    try:
        sheet = Sheet.objects.get(
            id=sheet_id,
            story__is_deleted=False,
            story__displayable=True,
            is_deleted=False
        )
    except Sheet.DoesNotExist:
        raise SheetDoesNotExists()

    return set(
        sheet.sheetanswer_set.all().values_list(
            'answer',
            flat=True
        )
    )


def get_valid_answer_info_with_random_quantity(answer: str, answer_responses: List[SheetAnswerResponseDTO]) -> (bool, int, int, int):
    """
    is_answer_valid: 정답 유무
    sheet_answer_id: quantity 를 통해 무작위로 결정된 SheetAnswer id
    next_sheet_path_id: quantity 를 통해 무작위로 결정된 NextSheetPath id
    next_sheet_id: quantity 를 통해 무작위로 결정된 다음 Sheet id
    """
    not_always_correct_answer_responses = [response for response in answer_responses if not response.is_always_correct]
    always_correct_answer_responses = [response for response in answer_responses if response.is_always_correct]
    matched_with_answer_of_answer_responses = [
        response for response in not_always_correct_answer_responses if
        response.answer.lower().replace(' ', '') == answer.lower().replace(' ', '')
    ]

    is_answer_valid = bool(len(matched_with_answer_of_answer_responses))
    sheet_answer_id = None

    # 정답이 있는 경우
    if is_answer_valid:
        quantity_next_sheet_id_and_next_sheet_path_ids = []
        # 정답들 가져오기
        for matched_with_answer_of_answer_response in matched_with_answer_of_answer_responses:
            if matched_with_answer_of_answer_response.next_sheet_quantity:
                quantity_next_sheet_id_and_next_sheet_path_ids += [
                    [
                        matched_with_answer_of_answer_response.id,
                        matched_with_answer_of_answer_response.next_sheet_path_id,
                        matched_with_answer_of_answer_response.next_sheet_id
                    ]
                ] * matched_with_answer_of_answer_response.next_sheet_quantity

        # 셔플하기
        random.shuffle(quantity_next_sheet_id_and_next_sheet_path_ids)

        # 값 가져오기
        sheet_answer_id, next_sheet_path_id, next_sheet_id = next(iter(quantity_next_sheet_id_and_next_sheet_path_ids), (None, None, None))

        # 정답에 경로가 없을 경우, 정답 id 만 정의
        if not sheet_answer_id:
            sheet_answer_id = matched_with_answer_of_answer_responses[0].id

        return is_answer_valid, sheet_answer_id, next_sheet_path_id, next_sheet_id

    # 항상 정답인 것이 있는 경우
    if always_correct_answer_responses:
        quantity_next_sheet_id_and_next_sheet_path_ids = []
        for always_correct_answer_response in always_correct_answer_responses:
            if always_correct_answer_response.next_sheet_quantity:
                quantity_next_sheet_id_and_next_sheet_path_ids += [
                    [
                        always_correct_answer_response.id,
                        always_correct_answer_response.next_sheet_path_id,
                        always_correct_answer_response.next_sheet_id,
                    ]
                ] * always_correct_answer_response.next_sheet_quantity

        # 셔플하기
        random.shuffle(quantity_next_sheet_id_and_next_sheet_path_ids)

        # 값 가져오기
        sheet_answer_id, next_sheet_path_id, next_sheet_id = next(iter(quantity_next_sheet_id_and_next_sheet_path_ids), (None, None, None))

        if not sheet_answer_id:
            sheet_answer_id = always_correct_answer_responses[0].id

        return True, sheet_answer_id, next_sheet_path_id, next_sheet_id

    return is_answer_valid, sheet_answer_id, None, None


def get_sheet_answer_with_next_path_responses(sheet_id: int) -> List[SheetAnswerResponseDTO]:
    try:
        sheet = Sheet.objects.get(
            id=sheet_id,
            story__is_deleted=False,
            story__displayable=True,
            is_deleted=False
        )
    except Sheet.DoesNotExist:
        raise SheetDoesNotExists()

    sheet_answer_responses = [
        SheetAnswerResponseDTO.of(sheet_answer_info_with_next_path) for
        sheet_answer_info_with_next_path
        in sheet.sheetanswer_set.all().values(
            'id',
            'answer',
            'answer_reply',
            'is_always_correct',
            'nextsheetpath',
            'next_sheet_paths__nextsheetpath__sheet_id',
            'next_sheet_paths__nextsheetpath__quantity',
        )
    ]

    return sheet_answer_responses


def get_sheet_solved_user_sheet_answer(user_id: int, sheet_id: int) -> Optional[UserSheetAnswerSolve]:
    running_sheet = get_running_sheet(sheet_id)
    try:
        return UserSheetAnswerSolve.objects.select_related(
            'next_sheet_path__answer',
        ).get(
            user_id=user_id,
            sheet_id=sheet_id,
            solved_sheet_version=running_sheet.version,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
        )
    except UserSheetAnswerSolve.DoesNotExist:
        return


def get_recent_played_sheet_by_story_id(user_id: int, story_id: int):
    user_sheet_answer_solve = UserSheetAnswerSolve.objects.select_related(
        'sheet',
    ).filter(
        user_id=user_id,
        story_id=story_id,
        sheet__is_deleted=False,
        start_time__isnull=False,
    ).order_by(
        '-start_time'
    ).first()
    if user_sheet_answer_solve:
        return user_sheet_answer_solve.sheet
    return


def get_story_email_subscription_emails(story_id: int, user_id: int):
    return list(
        StoryEmailSubscription.objects.filter(
            story_id=story_id,
            respondent_user_id=user_id,
        ).values_list(
            'email',
            flat=True
        )
    )


def get_story_slack_subscription_slack_webhook_urls(story_id: int, user_id: int):
    return list(
        StorySlackSubscription.objects.filter(
            story_id=story_id,
            respondent_user_id=user_id,
        ).values_list(
            'slack_webhook_url',
            flat=True
        )
    )


def create_story_like(story_id: int, user_id: int):
    with transaction.atomic():
        story_like, is_created = StoryLike.objects.get_or_create(
            story_id=story_id,
            user_id=user_id,
        )
        if not is_created:
            story_like.is_deleted = False
            story_like.save(update_fields=['is_deleted', 'updated_at'])
        update_story_total_like_count(story_id)
    return story_like


def delete_story_like(story_id: int, user_id: int):
    with transaction.atomic():
        story_like = StoryLike.objects.get(
            story_id=story_id,
            user_id=user_id,
            is_deleted=False,
        )
        story_like.is_deleted = True
        story_like.save(update_fields=['is_deleted', 'updated_at'])
        update_story_total_like_count(story_id)
    return story_like


def update_story_total_like_count(story_id: int):
    story = Story.objects.get(id=story_id)
    story.like_count = StoryLike.get_active_story_like_count(story_id)
    story.save(update_fields=['like_count'])


@transaction.atomic
def reset_user_story_sheet_answer_solves(user_id: int, story_id: int):
    """
    유저의 모든 시트 답안을 백업 후,
    유저의 모든 시트 답안을 초기화 합니다.
    """
    user_sheet_answer_solves = UserSheetAnswerSolve.objects.filter(
        user_id=user_id,
        story_id=story_id,
    )
    user_sheet_answer_solves_values = user_sheet_answer_solves.values()

    user_sheet_answer_solve_history_qs = UserSheetAnswerSolveHistory.objects.filter(
        user_id=user_id,
        story_id=story_id,
    )
    max_group_id = get_max_int_from_queryset(user_sheet_answer_solve_history_qs, 'group_id')

    if user_sheet_answer_solves:
        bulk_create_user_sheet_answer_solve_history_list = []
        for user_sheet_answer_solve_value in user_sheet_answer_solves_values:
            user_sheet_answer_solve_history = UserSheetAnswerSolveHistory()
            for key, value in user_sheet_answer_solve_value.items():
                setattr(user_sheet_answer_solve_history, key, value)
            setattr(user_sheet_answer_solve_history, 'group_id', max_group_id + 1 if max_group_id else 1)
            bulk_create_user_sheet_answer_solve_history_list.append(
                user_sheet_answer_solve_history
            )
        UserSheetAnswerSolveHistory.objects.bulk_create(
            bulk_create_user_sheet_answer_solve_history_list
        )
        user_sheet_answer_solves.delete()
        return True

    return False


def create_wrong_answer(user_id: int, story_id: int, sheet_id: int, wrong_answer: str):
    return WrongAnswer.objects.create(
        user_id=user_id,
        story_id=story_id,
        sheet_id=sheet_id,
        answer=wrong_answer,
    )


def get_user_sheet_answer_solve_histories(user_id: int, story_id: int) -> List[UserSheetAnswerSolveHistoryItemDTO]:
    return [
        UserSheetAnswerSolveHistoryItemDTO.of(user_sheet_answer_solve_history)
        for user_sheet_answer_solve_history in UserSheetAnswerSolveHistory.objects.select_related(
            'sheet',
        ).filter(
            user_id=user_id,
            story_id=story_id,
        ).order_by(
            '-group_id',
            '-id',
        )
    ]
