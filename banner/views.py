from rest_framework.views import APIView
from rest_framework.response import Response

from banner.dtos import BannerListItemDTO
from banner.services import get_active_banners


class BannerListAPIView(APIView):
    def get(self, request):
        active_banners_order_by_sequence_desc = get_active_banners(order_by=['-sequence'])
        return Response(
            data={
                'banners': [
                    BannerListItemDTO.of(banner).to_dict()
                    for banner in active_banners_order_by_sequence_desc
                ]
            },
            status=200,
        )
