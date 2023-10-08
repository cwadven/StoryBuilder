from django.db.models import (
    Q,
    QuerySet,
)
from typing import Any

from story.models import (
    Sheet,
    Story,
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
