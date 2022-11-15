import attr

from story.models import Sheet


@attr.s
class PlayingSheetDTO(object):
    id = attr.ib(type=int)
    title = attr.ib(type=str)
    question = attr.ib(type=str)
    image = attr.ib(type=str)
    background_image = attr.ib(type=str)

    @classmethod
    def of(cls, sheet: Sheet):
        return cls(
            id=sheet.id,
            title=sheet.title,
            question=sheet.question,
            image=sheet.image,
            background_image=sheet.background_image,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)
