from rest_framework.views import APIView
from rest_framework.response import Response

from common_decorator import custom_login_required_for_method
from point.dtos import UserPointInfoResponseDTO
from point.services import get_user_available_total_point


class UserPointAPIView(APIView):
    @custom_login_required_for_method
    def get(self, request):
        return Response(
            data=UserPointInfoResponseDTO(
                total_point=get_user_available_total_point(request.user.id)
            ).to_dict(),
            status=200
        )
