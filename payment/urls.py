from django.urls import path

from payment.views import (
    KakaoPayApproveForBuyPointAPIView,
    KakaoPayCancelForBuyPointAPIView,
    KakaoPayFailForBuyPointAPIView,
    KakaoPayReadyForBuyPointAPIView,
)

app_name = 'payment'


urlpatterns = [
    path('point/buy', KakaoPayReadyForBuyPointAPIView.as_view(), name='point_buy'),
    path('point/approve/<int:order_id>', KakaoPayApproveForBuyPointAPIView.as_view(), name='point_approve'),
    path('point/cancel/<int:order_id>', KakaoPayCancelForBuyPointAPIView.as_view(), name='point_cancel'),
    path('point/fail/<int:order_id>', KakaoPayFailForBuyPointAPIView.as_view(), name='point_fail'),
]
