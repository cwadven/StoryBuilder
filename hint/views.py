from rest_framework.response import Response
from rest_framework.views import APIView

from common_decorator import custom_login_required_for_method
from story.services import get_running_sheet
from .dtos import UserSheetHintInfosResponse
from .services import get_sheet_hint_infos


class SheetHintAPIView(APIView):
    @custom_login_required_for_method
    def get(self, request, sheet_id):
        get_running_sheet(sheet_id)

        sheet_hint_infos = get_sheet_hint_infos(request.user.id, sheet_id)
        user_sheet_hint_infos = UserSheetHintInfosResponse(
            user_sheet_hint_infos=sheet_hint_infos,
        ).to_dict()
        return Response(user_sheet_hint_infos, status=200)
