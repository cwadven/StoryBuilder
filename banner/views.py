from rest_framework.views import APIView
from rest_framework.response import Response

from banner.dtos import BannerListItemDTO, BannerDetailItemDTO
from banner.models import Banner
from banner.services import get_active_banners
from config.common.exception_codes import BannerDoesNotExists


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


class BannerDetailAPIView(APIView):
    def get(self, request, banner_id):
        try:
            banner = get_active_banners().get(id=banner_id)
        except Banner.DoesNotExist:
            raise BannerDoesNotExists()

        return Response(
            data=BannerDetailItemDTO.of(banner).to_dict(),
            status=200,
        )
