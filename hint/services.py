from hint.dtos import UserSheetHintInfoDTO
from hint.models import SheetHint, UserSheetHintHistory


def get_user_available_sheet_hints(user, sheet_id: int) -> list:
    sheet_hints = SheetHint.objects.filter(
        sheet_id=sheet_id,
        is_deleted=False,
    ).order_by(
        'sequence',
    )
    user_accessible_sheet_hint_ids = UserSheetHintHistory.objects.select_related(
        'sheet_hint',
    ).filter(
        user=user,
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
