import attr
from collections import defaultdict
from typing import List

from story.constants import StoryLevel
from story.models import Sheet, UserSheetAnswerSolve, Story, PopularStory, UserSheetAnswerSolveHistory


@attr.s
class SheetAnswerResponseDTO(object):
    id = attr.ib(type=int)
    answer = attr.ib(type=str)
    answer_reply = attr.ib(type=str)
    is_always_correct = attr.ib(type=bool)
    next_sheet_path_id = attr.ib(type=int)
    next_sheet_id = attr.ib(type=int)
    next_sheet_quantity = attr.ib(type=int)

    @classmethod
    def of(cls, sheet_answer: dict):
        return cls(
            id=sheet_answer['id'],
            answer=sheet_answer['answer'].replace(' ', ''),
            answer_reply=sheet_answer['answer_reply'],
            is_always_correct=sheet_answer['is_always_correct'],
            next_sheet_path_id=sheet_answer['nextsheetpath'],
            next_sheet_id=sheet_answer['next_sheet_paths__nextsheetpath__sheet_id'],
            next_sheet_quantity=sheet_answer['next_sheet_paths__nextsheetpath__quantity'],
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class PreviousSheetInfoDTO(object):
    sheet_id = attr.ib(type=int)
    title = attr.ib(type=str)

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class PlayingSheetInfoDTO(object):
    sheet_id = attr.ib(type=int)
    title = attr.ib(type=str)
    question = attr.ib(type=str)
    image = attr.ib(type=str)
    background_image = attr.ib(type=str)
    previous_sheet_infos = attr.ib(type=List[PreviousSheetInfoDTO])
    next_sheet_id = attr.ib(type=int)
    answer = attr.ib(type=str)
    answer_reply = attr.ib(type=str)
    is_solved = attr.ib(type=bool)

    @classmethod
    def of(cls, sheet: Sheet, user_sheet_answer_solve: UserSheetAnswerSolve = None, previous_sheet_infos: list = None):
        """
        user_sheet_answer_solve의 next_sheet_path__answer 필요
        answer
        """
        return cls(
            sheet_id=sheet.id,
            title=sheet.title,
            question=sheet.question,
            image=sheet.image,
            background_image=sheet.background_image,
            previous_sheet_infos=previous_sheet_infos,
            next_sheet_id=user_sheet_answer_solve.next_sheet_path.sheet_id if (user_sheet_answer_solve and user_sheet_answer_solve.next_sheet_path) else None,
            answer=user_sheet_answer_solve.answer if user_sheet_answer_solve else None,
            answer_reply=user_sheet_answer_solve.solved_sheet_answer.answer_reply if (user_sheet_answer_solve and user_sheet_answer_solve.solved_sheet_answer) else None,
            is_solved=bool(user_sheet_answer_solve),
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class StoryListItemDTO(object):
    id = attr.ib(type=int)
    title = attr.ib(type=str)
    description = attr.ib(type=str)
    image = attr.ib(type=str)
    background_image = attr.ib(type=str)

    @classmethod
    def of(cls, story: Story):
        return cls(
            id=story.id,
            title=story.title,
            description=story.description,
            image=story.image,
            background_image=story.background_image,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class StoryPopularListItemDTO(object):
    story_id = attr.ib(type=int)
    title = attr.ib(type=str)
    image = attr.ib(type=str)

    @classmethod
    def of(cls, popular_story: PopularStory):
        return cls(
            story_id=popular_story.story.id,
            title=popular_story.story.title,
            image=popular_story.story.image,
        )

    @classmethod
    def by_story(cls, story: Story):
        return cls(
            story_id=story.id,
            title=story.title,
            image=story.image,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class StoryDetailItemDTO(object):
    id = attr.ib(type=int)
    title = attr.ib(type=str)
    description = attr.ib(type=str)
    image = attr.ib(type=str)
    background_image = attr.ib(type=str)
    played_count = attr.ib(type=int)
    like_count = attr.ib(type=int)
    review_rate = attr.ib(type=float)
    playing_point = attr.ib(type=int)
    free_to_play_sheet_count = attr.ib(type=int)
    level = attr.ib(type=str)
    is_liked = attr.ib(type=bool)

    @classmethod
    def of(cls, story: Story, is_liked: bool):
        return cls(
            id=story.id,
            title=story.title,
            description=story.description,
            image=story.image,
            background_image=story.background_image,
            played_count=story.played_count,
            like_count=story.like_count,
            review_rate=story.review_rate,
            playing_point=story.playing_point,
            free_to_play_sheet_count=story.free_to_play_sheet_count,
            level=StoryLevel(story.level).selector,
            is_liked=is_liked,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class UserSheetAnswerSolveHistoryItemDTO(object):
    group_id = attr.ib(type=int)
    sheet_title = attr.ib(type=str)
    sheet_question = attr.ib(type=str)
    user_answer = attr.ib(type=str)
    solving_status = attr.ib(type=str)
    start_time = attr.ib(type=str)
    solved_time = attr.ib(type=str)

    @classmethod
    def of(cls, user_sheet_answer_solve_history: UserSheetAnswerSolveHistory):
        start_time = user_sheet_answer_solve_history.start_time.strftime('%Y-%m-%d %H:%M:%S') if user_sheet_answer_solve_history.start_time else ''
        solved_time = user_sheet_answer_solve_history.solved_time.strftime('%Y-%m-%d %H:%M:%S') if user_sheet_answer_solve_history.solved_time else ''
        return cls(
            group_id=user_sheet_answer_solve_history.group_id,
            sheet_title=user_sheet_answer_solve_history.sheet.title,
            sheet_question=user_sheet_answer_solve_history.sheet.question,
            user_answer=user_sheet_answer_solve_history.answer,
            solving_status=user_sheet_answer_solve_history.solving_status,
            start_time=start_time,
            solved_time=solved_time,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class GroupedSheetAnswerSolveDTO(object):
    group_id = attr.ib(type=int)
    sheet_answer_solve = attr.ib(type=List[UserSheetAnswerSolveHistoryItemDTO])

    @classmethod
    def from_histories(cls, user_sheet_answer_solve_history_items: List[UserSheetAnswerSolveHistoryItemDTO]):
        grouped_data = defaultdict(list)

        for history_item in user_sheet_answer_solve_history_items:
            grouped_data[history_item.group_id].append(history_item.to_dict())

        return [cls(group_id=group_id, sheet_answer_solve=solve_list) for group_id, solve_list in grouped_data.items()]

    def to_dict(self):
        return attr.asdict(self, recurse=True)
