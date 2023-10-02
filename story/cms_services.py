from django.db.models import Q
from typing import Any

from story.models import Story


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
