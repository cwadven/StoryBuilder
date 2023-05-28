from django.http import JsonResponse
from django.urls import path

from payment.views import (
    KakaoPayApproveForBuyPointAPIView,
    KakaoPayCancelForBuyPointAPIView,
    KakaoPayReadyForBuyPointAPIView,
)

app_name = 'payment'


urlpatterns = [
    path('test_fail', lambda request: JsonResponse({'message': 'fail'}), name='test'),
    path('point/buy', KakaoPayReadyForBuyPointAPIView.as_view(), name='point_buy'),
    path('point/approve/<int:order_id>', KakaoPayApproveForBuyPointAPIView.as_view(), name='point_approve'),
    path('point/cancel/<int:order_id>', KakaoPayCancelForBuyPointAPIView.as_view(), name='point_cancel'),
]
