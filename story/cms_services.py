from django.db.models import (
    Q,
    QuerySet,
)
from typing import (
    Any,
    Dict,
    List,
)

from story.models import (
    Sheet,
    Story,
    SheetAnswer, NextSheetPath,
)


def get_stories_qs():
    return Story.objects.all()


def get_story_search_filter(search_type: str, search_value: Any) -> Q:
    if search_type == 'title':
        return Q(title__icontains=search_value)
    elif search_type == 'author':
        return Q(author__nickname__icontains=search_value)
    elif search_type == 'description':
        return Q(description__icontains=search_value)
    return Q()


def get_active_sheets(story_id: int) -> QuerySet[Sheet]:
    return Sheet.objects.filter(
        story_id=story_id,
        is_deleted=False
    )


def get_sheet_answer_ids_by_sheet_ids(sheet_ids: List[int]) -> Dict[int, List[int]]:
    if not sheet_ids:
        return {}

    answer_ids_by_sheet_id = {sheet_id: [] for sheet_id in sheet_ids}

    sheet_answers_from_db = SheetAnswer.objects.filter(
        sheet_id__in=sheet_ids,
    )
    for sheet_answer in sheet_answers_from_db:
        answer_ids_by_sheet_id[sheet_answer.sheet_id].append(sheet_answer.id)

    return answer_ids_by_sheet_id


def get_sheet_answers_by_sheet_ids(sheet_ids: List[int]) -> List[SheetAnswer]:
    if not sheet_ids:
        return []
    return list(
        SheetAnswer.objects.filter(
            sheet_id__in=sheet_ids,
        )
    )


def get_next_sheet_paths_by_sheet_answer_ids(answer_ids: List[int]) -> Dict[int, List[NextSheetPath]]:
    if not answer_ids:
        return {}

    next_sheet_path_by_answer_id = {}
    for answer_id in answer_ids:
        next_sheet_path_by_answer_id[answer_id] = []
    for next_sheet_path in NextSheetPath.objects.filter(answer__in=answer_ids):
        next_sheet_path_by_answer_id[next_sheet_path.answer_id].append(next_sheet_path)
    return next_sheet_path_by_answer_id
