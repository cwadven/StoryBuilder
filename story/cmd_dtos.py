import attr
from datetime import datetime

from typing import List

from story.models import Story


@attr.s
class CMSStoryListItemDTO(object):
    id = attr.ib(type=int)
    title = attr.ib(type=str)
    description = attr.ib(type=str)
    image = attr.ib(type=str)
    background_image = attr.ib(type=str)
    nickname = attr.ib(type=str)
    played_count = attr.ib(type=int)
    like_count = attr.ib(type=int)
    view_count = attr.ib(type=int)
    review_rate = attr.ib(type=float)
    playing_point = attr.ib(type=int)
    level = attr.ib(type=int)
    displayable = attr.ib(type=bool)
    is_deleted = attr.ib(type=bool)
    is_secret = attr.ib(type=bool)
    created_at = attr.ib(type=datetime)
    updated_at = attr.ib(type=datetime)

    @classmethod
    def of(cls, story: Story):
        return cls(
            id=story.id,
            title=story.title,
            description=story.description,
            image=story.image,
            background_image=story.background_image,
            nickname=story.author.nickname,
            played_count=story.played_count,
            like_count=story.like_count,
            view_count=story.view_count,
            review_rate=story.review_rate,
            playing_point=story.playing_point,
            level=story.level,
            is_deleted=story.is_deleted,
            displayable=story.displayable,
            is_secret=story.is_secret,
            created_at=story.created_at,
            updated_at=story.updated_at,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class CMSStoryListResponse(object):
    total_count = attr.ib(type=int)
    stories = attr.ib(type=List[CMSStoryListItemDTO])

    def to_dict(self):
        return attr.asdict(self, recurse=True)
