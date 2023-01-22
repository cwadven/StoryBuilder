import attr

from hint.models import SheetHint


@attr.s
class UserSheetHintInfoDTO(object):
    id = attr.ib(type=int)
    hint = attr.ib(type=str)
    point = attr.ib(type=int)
    image = attr.ib(type=str)
    has_history = attr.ib(type=bool)

    @classmethod
    def of(cls, sheet_hint: SheetHint, has_history: bool):
        return cls(
            id=sheet_hint.id,
            hint=sheet_hint.hint if has_history else '',
            point=sheet_hint.point,
            image=sheet_hint.image if has_history else '',
            has_history=has_history,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class UserSheetHintInfosResponse(object):
    user_sheet_hint_infos = attr.ib(type=list)

    def to_dict(self):
        return attr.asdict(self, recurse=True)
