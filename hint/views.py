from rest_framework.response import Response
from rest_framework.views import APIView

from common_decorator import custom_login_required_for_method, mandatories
from story.services import get_running_sheet
from .dtos import UserSheetHintInfosResponse, UserSheetHintInfoDTO
from .services import get_sheet_hint_infos, give_sheet_hint_information, get_available_sheet_hint


class SheetHintAPIView(APIView):
    @custom_login_required_for_method
    def get(self, request, sheet_id):
        get_running_sheet(sheet_id)

        sheet_hint_infos = get_sheet_hint_infos(request.user.id, sheet_id)
        user_sheet_hint_infos = UserSheetHintInfosResponse(
            user_sheet_hint_infos=sheet_hint_infos,
        ).to_dict()
        return Response(user_sheet_hint_infos, status=200)

    @mandatories('sheet_hint_id')
    @custom_login_required_for_method
    def post(self, request, sheet_id, m):
        get_running_sheet(sheet_id)
        available_sheet_hint = get_available_sheet_hint(m['sheet_hint_id'])

        sheet_hint = give_sheet_hint_information(
            user_id=request.user.id,
            sheet_hint_id=available_sheet_hint.id,
        )
        sheet_hint_info = UserSheetHintInfoDTO.of(sheet_hint, True).to_dict()
        return Response(sheet_hint_info, status=200)
