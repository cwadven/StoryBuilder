import attr
from datetime import datetime

from typing import (
    List,
    Type,
)

from story.models import (
    Sheet,
    SheetAnswer,
    Story,
)


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


@attr.s
class CMSStorySheetMapItemDTO(object):
    id = attr.ib(type=int)
    title = attr.ib(type=str)
    question = attr.ib(type=str)
    image = attr.ib(type=str)
    background_image = attr.ib(type=str)
    hint_count = attr.ib(type=int)
    answer_ids = attr.ib(type=List[int])

    @classmethod
    def of(cls, sheet: Sheet, hint_count: int, answer_ids: List[int]):
        return cls(
            id=sheet.id,
            title=sheet.title,
            question=sheet.question,
            image=sheet.image,
            background_image=sheet.background_image,
            hint_count=hint_count,
            answer_ids=answer_ids,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class CMSStorySheetMapResponse(object):
    sheets = attr.ib(type=List[CMSStorySheetMapItemDTO])

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class CMSStorySheetAnswerMapItemDTO(object):
    id = attr.ib(type=int)
    sheet_id = attr.ib(type=Type[int])
    answer = attr.ib(type=str)
    answer_reply = attr.ib(type=str)
    is_always_correct = attr.ib(type=bool)

    @classmethod
    def of(cls, sheet_answer: SheetAnswer):
        return cls(
            id=sheet_answer.id,
            sheet_id=sheet_answer.sheet_id,
            answer=sheet_answer.answer,
            answer_reply=sheet_answer.answer_reply,
            is_always_correct=sheet_answer.is_always_correct,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class CMSStorySheetAnswerMapResponse(object):
    answers = attr.ib(type=List[CMSStorySheetAnswerMapItemDTO])

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class CMSStoryAnswerNextPathItemDTO(object):
    sheet_id = attr.ib(type=int)
    quantity = attr.ib(type=int)


@attr.s
class CMSStoryAnswerNextPathMapItemDTO(object):
    answer_id = attr.ib(type=int)
    next_paths = attr.ib(type=List[CMSStoryAnswerNextPathItemDTO])

    @classmethod
    def of(cls, sheet_answer: SheetAnswer, next_paths: List[CMSStoryAnswerNextPathItemDTO]):
        return cls(
            answer_id=sheet_answer.id,
            next_paths=next_paths,
        )


@attr.s
class CMSStoryAnswerNextPathMapResponse(object):
    answer_next_paths = attr.ib(type=List[CMSStoryAnswerNextPathMapItemDTO])

    def to_dict(self):
        return attr.asdict(self, recurse=True)
