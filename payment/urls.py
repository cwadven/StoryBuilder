from django.urls import path

from payment.views import (
    KakaoPayApproveForBuyPointAPIView,
    KakaoPayCancelForBuyPointAPIView,
    KakaoPayFailForBuyPointAPIView,
    KakaoPayReadyForBuyPointAPIView,
    PointProductListAPIView,
)

app_name = 'payment'


urlpatterns = [
    path('point', PointProductListAPIView.as_view(), name='points'),
    path('point/buy/kakao', KakaoPayReadyForBuyPointAPIView.as_view(), name='point_buy'),
    path('point/approve/kakao/<int:order_id>', KakaoPayApproveForBuyPointAPIView.as_view(), name='point_approve'),
    path('point/cancel/kakao/<int:order_id>', KakaoPayCancelForBuyPointAPIView.as_view(), name='point_cancel'),
    path('point/fail/kakao/<int:order_id>', KakaoPayFailForBuyPointAPIView.as_view(), name='point_fail'),
]
