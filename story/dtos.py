import attr
from typing import List, Dict

from story.models import Sheet, UserSheetAnswerSolve, Story


@attr.s
class SheetAnswerResponseDTO(object):
    id = attr.ib(type=int)
    answer = attr.ib(type=str)
    answer_reply = attr.ib(type=str)
    next_sheet_path_id = attr.ib(type=int)
    next_sheet_id = attr.ib(type=int)
    next_sheet_quantity = attr.ib(type=int)

    @classmethod
    def of(cls, sheet_answer: dict):
        return cls(
            id=sheet_answer['id'],
            answer=sheet_answer['answer'].replace(' ', ''),
            answer_reply=sheet_answer['answer_reply'],
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
