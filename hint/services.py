from django.db import transaction

from config.common.exception_codes import UserSheetHintHistoryAlreadyExists, SheetHintDoesNotExists, NotEnoughUserPoints
from hint.consts import GIVE_USER_HINT_POINT
from hint.dtos import UserSheetHintInfoDTO
from hint.models import SheetHint, UserSheetHintHistory
from point.services import use_point


def get_sheet_hint_infos(user_id: int, sheet_id: int) -> list:
    sheet_hints = SheetHint.objects.filter(
        sheet_id=sheet_id,
        is_deleted=False,
    ).order_by(
        'sequence',
    )
    user_accessible_sheet_hint_ids = UserSheetHintHistory.objects.select_related(
        'sheet_hint',
    ).filter(
        user_id=user_id,
        sheet_hint__sheet_id=sheet_id,
    ).values_list(
        'sheet_hint_id',
        flat=True,
    )

    user_available_sheet_hint_infos = []
    for sheet_hint in sheet_hints:
        user_available_sheet_hint_infos.append(
            UserSheetHintInfoDTO.of(
                sheet_hint=sheet_hint,
                has_history=sheet_hint.id in user_accessible_sheet_hint_ids,
            ).to_dict()
        )
    return user_available_sheet_hint_infos


def give_sheet_hint_information(user_id: int, sheet_hint_id: int) -> SheetHint:
    with transaction.atomic():
        user_sheet_hint_history, is_created = UserSheetHintHistory.objects.select_related(
            'sheet_hint',
        ).get_or_create(
            user_id=user_id,
            sheet_hint_id=sheet_hint_id,
        )
        if not is_created:
            raise UserSheetHintHistoryAlreadyExists

        use_point(
            user_id=user_id,
            point=user_sheet_hint_history.sheet_hint.point,
            description=GIVE_USER_HINT_POINT
        )

    return user_sheet_hint_history.sheet_hint


def get_available_sheet_hint(sheet_hint_id: int) -> SheetHint:
    try:
        return SheetHint.objects.get(
            id=sheet_hint_id,
            is_deleted=False,
        )
    except SheetHint.DoesNotExist:
        raise SheetHintDoesNotExists
