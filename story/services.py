from datetime import datetime
import random
from typing import List, Optional

from django.db import transaction
from django.db.models import Q

from config.common.exception_codes import StartingSheetDoesNotExists, SheetDoesNotExists, SheetNotAccessibleException, \
    StoryDoesNotExists
from story.dtos import SheetAnswerResponseDTO
from story.models import Sheet, UserSheetAnswerSolve, StoryEmailSubscription, StoryLike, Story, PopularStory


def get_active_stories(search='', start_row=None, end_row=None) -> List[Story]:
    qs = Story.objects.filter(
        is_deleted=False,
        displayable=True,
    ).order_by('-id')

    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

    if start_row is not None and end_row is not None:
        return list(qs[start_row:end_row])
    return list(qs)


def get_active_popular_stories() -> List[PopularStory]:
    qs = PopularStory.objects.filter(
        story__is_deleted=False,
        story__displayable=True,
        is_deleted=False,
    ).order_by('rank')
    return list(qs)


def get_active_story_by_id(story_id: int) -> Story:
    try:
        return Story.objects.get(
            id=story_id,
            is_deleted=False,
            displayable=True,
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
    """
    try:
        user_sheet_answer_solve = UserSheetAnswerSolve.objects.get(
            user_id=user_id,
            next_sheet_path__sheet_id=sheet_id,
            solving_status=UserSheetAnswerSolve.SOLVING_STATUS_CHOICES[1][0],
        )
    except UserSheetAnswerSolve.DoesNotExist:
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
    정답유무, sheet_answer_id, next_sheet_id(랜덤한 quantity로 구한 것)
    """
    is_answer_valid = answer.replace(' ', '') in map(lambda answer_response: answer_response.answer.replace(' ', ''), answer_responses)
    sheet_answer_id = None

    if is_answer_valid:
        quantity_next_sheet_id_and_next_sheet_path_ids = []
        # 정답들 가져오기
        filtered_answer_responses = list(
            filter(
                lambda answer_response: answer_response.answer.replace(' ', '') == answer.replace(' ', ''),
                answer_responses
            )
        )
        for filtered_answer_response in filtered_answer_responses:
            if filtered_answer_response.next_sheet_quantity:
                quantity_next_sheet_id_and_next_sheet_path_ids += [
                   [filtered_answer_response.next_sheet_path_id, filtered_answer_response.next_sheet_id]
                ] * filtered_answer_response.next_sheet_quantity
        # 셔플하기
        random.shuffle(quantity_next_sheet_id_and_next_sheet_path_ids)
        # 값 가져오기
        first_filtered_answer_response = next(iter(filtered_answer_responses), None)
        sheet_answer_id = first_filtered_answer_response.id if first_filtered_answer_response else None
        next_sheet_path_id, next_sheet_id = next(iter(quantity_next_sheet_id_and_next_sheet_path_ids), (None, None))
        # 정답유무, sheet_answer_id, next_sheet_path_id, next_sheet_id
        return is_answer_valid, sheet_answer_id, next_sheet_path_id, next_sheet_id
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
