from rest_framework.views import APIView
from rest_framework.response import Response

from common_decorator import custom_login_required_for_method
from config.common.exception_codes import PointProductNotExists, OrderNotExists
from payment.consts import PaymentType
from payment.dtos import KakaoPayReadyResponseDTO
from payment.helpers import KakaoPay, KakaoPayPointHandler
from payment.models import PointProduct, Order, OrderGivePoint


class KakaoPayReadyForBuyPointAPIView(APIView):
    @custom_login_required_for_method
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        payment_type = request.POST.get('payment_type')

        try:
            point_product = PointProduct.objects.get_actives().get(id=product_id)
        except PointProduct.DoesNotExist:
            raise PointProductNotExists()

        order = point_product.create_order(
            user_id=request.user.id,
            payment=payment_type,
            quantity=quantity,
        )
        kakao_pay = KakaoPay(KakaoPayPointHandler(order_id=order.id))
        kakao_pay_response_dto = KakaoPayReadyResponseDTO.from_dict(
            kakao_pay.ready_to_pay(
                order_id=str(order.id),
                user_id=str(request.user.id),
                product_name=point_product.title,
                quantity=str(quantity),
                total_amount=str(order.total_user_paid_price),
                tax_free_amount=str(0),
            )
        )
        order.tid = kakao_pay_response_dto.tid
        order.save(update_fields=['tid'])
        return Response(
            data=kakao_pay_response_dto.to_dict(),
            status=200
        )


class KakaoPayApproveForBuyPointAPIView(APIView):
    def get(self, request, order_id):
        pg_token = request.GET.get('pg_token')

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise OrderNotExists()

        kakao_pay = KakaoPay(KakaoPayPointHandler(order_id=order.id))
        response = kakao_pay.approve_payment(tid=order.tid, pg_token=pg_token, order_id=order.id, user_id=order.user_id)
        if response['payment_method_type'] == 'MONEY':
            order.approved(PaymentType.KAKAOPAY_MONEY.value)
        else:
            order.approved(PaymentType.KAKAOPAY_CARD.value)

        try:
            order_give_point = OrderGivePoint.objects.get(order_id=order.id)
            order_give_point.give()
        except OrderGivePoint.DoesNotExist:
            raise OrderNotExists()

        return Response(
            data={'message': '결제가 완료되었습니다.'},
            status=200
        )
