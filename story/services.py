import random
from typing import List

from config.common.exception_codes import StartingSheetDoesNotExists, SheetDoesNotExists
from story.dtos import SheetAnswerResponseDTO
from story.models import Sheet


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


def get_valid_answer_info_with_random_quantity(answer: str, answer_responses: List[SheetAnswerResponseDTO]) -> (bool, int, int):
    """
    정답유무, sheet_answer_id, next_sheet_id(랜덤한 quantity로 구한 것)
    """
    is_answer_valid = answer.replace(' ', '') in map(lambda answer_response: answer_response.answer.replace(' ', ''), answer_responses)

    if is_answer_valid:
        quantity_next_sheet_ids = []
        # 정답들 가져오기
        filtered_answer_responses = list(filter(lambda answer_response: answer_response.answer.replace(' ', '') == answer.replace(' ', ''), answer_responses))
        for filtered_answer_response in filtered_answer_responses:
            quantity_next_sheet_ids += [filtered_answer_response.next_sheet_id] * filtered_answer_response.next_sheet_quantity
        # 셔플하기
        random.shuffle(quantity_next_sheet_ids)
        # 값을 가져오기
        # 정답유무, sheet_answer_id, next_sheet_id
        return is_answer_valid, filtered_answer_responses[0].id, quantity_next_sheet_ids[0]
    return is_answer_valid, None, None


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
            'next_sheet_paths__nextsheetpath__sheet_id',
            'next_sheet_paths__nextsheetpath__quantity',
        )
    ]

    return sheet_answer_responses
