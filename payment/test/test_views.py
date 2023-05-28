from datetime import datetime
import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time

from config.common.exception_codes import PointProductNotExists, OrderNotExists
from config.test_helper.helper import LoginMixin
from payment.consts import PaymentType, ProductType, OrderStatus, PointGivenStatus
from payment.models import PointProduct, OrderGivePoint, Order


@freeze_time('2021-01-01')
class KakaoPayReadyForBuyPointAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(KakaoPayReadyForBuyPointAPIViewTestCase, self).setUp()
        self.point_product_1000 = PointProduct.objects.create(
            title='1000 포인트 상품',
            description='1000 포인트 상품입니다.',
            price=1000,
            point=1000,
            is_active=True,
            start_time=datetime(2021, 1, 1),
            end_time=datetime(2021, 12, 31),
            quantity=100,
        )

    @patch('payment.views.KakaoPay.ready_to_pay')
    def test_kakao_pay_ready_for_buy_point_api_when_success(self, mock_ready_to_pay):
        # Given:
        self.login()
        data = {
            'product_id': self.point_product_1000.id,
            'quantity': 1,
            'payment_type': PaymentType.KAKAOPAY.value,
        }
        # And: 모킹
        mock_ready_to_pay.return_value = {
            'tid': 'T469b847306d7b2dc394',
            'tms_result': False,
            'next_redirect_app_url': 'https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/aInfo',
            'next_redirect_mobile_url': 'https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/mInfo',
            'next_redirect_pc_url': 'https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/info',
            'android_app_scheme': 'kakaotalk://kakaopay/pg?url=https://online-pay.kakao.com/pay/mockup/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46',
            'ios_app_scheme': 'kakaotalk://kakaopay/pg?url=https://online-pay.kakao.com/pay/mockup/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46',
            'created_at': '2023-05-21T15:20:55'
        }

        # When:
        response = self.c.post(reverse('payment:point_buy'), data=data)
        content = json.loads(response.content)

        # Then: 주문 준비 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(content['tid'], 'T469b847306d7b2dc394')
        self.assertEqual(
            content['next_redirect_mobile_url'],
            'https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/mInfo'
        )

    def test_kakao_pay_ready_for_buy_point_api_when_fail_due_to_point_product_not_exists(self):
        # Given:
        self.login()
        # And: 존재하지 않는 상품 id
        data = {
            'product_id': 9999,
            'quantity': 1,
            'payment_type': PaymentType.KAKAOPAY.value,
        }

        # When:
        response = self.c.post(reverse('payment:point_buy'), data=data)
        content = json.loads(response.content)

        # Then: 없는 상품으로 실패
        self.assertEqual(response.status_code, PointProductNotExists.status_code)
        self.assertEqual(content['message'], PointProductNotExists.default_detail)


@freeze_time('2021-01-01')
class KakaoPayApproveForBuyPointAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(KakaoPayApproveForBuyPointAPIViewTestCase, self).setUp()
        self.point_product_1000 = PointProduct.objects.create(
            title='1000 포인트 상품',
            description='1000 포인트 상품입니다.',
            price=1000,
            point=1000,
            is_active=True,
            start_time=datetime(2021, 1, 1),
            end_time=datetime(2021, 12, 31),
            quantity=100,
        )

    @patch('payment.views.KakaoPay.approve_payment')
    def test_kakao_pay_approve_for_buy_point_api_when_success(self, mock_approve_payment):
        # Given:
        self.login()
        data = {
            'pg_token': 'test_token',
        }
        # And: 주문 생성
        order = Order.objects.create(
            user_id=self.c.user.id,
            product_type=ProductType.POINT.value,
            tid='T469b847306d7b2dc394',
            total_price=1000,
            total_product_price=1000,
            total_user_paid_price=1000,
            total_discount_price=0,
            total_product_discount_price=0,
            status=OrderStatus.READY.value,
            payment=PaymentType.KAKAOPAY.value,
        )
        # And: OrderGivePoint 생성
        OrderGivePoint.objects.create(
            order_id=order.id,
            user_id=self.c.user.id,
            status=PointGivenStatus.READY.value,
            point=1000,
        )
        # And: 모킹
        mock_approve_payment.return_value = {
            "aid": "A469b85a306d7b2dc395",
            "tid": "T469b847306d7b2dc394",
            "cid": "TC0ONETIME",
            "partner_order_id": "test1",
            "partner_user_id": "1",
            "payment_method_type": "MONEY",
            "item_name": "1000 포인트",
            "item_code": "",
            "quantity": 1,
            "amount": {
                "total": 1000,
                "tax_free": 0,
                "vat": 91,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "created_at": "2023-05-21T15:20:55",
            "approved_at": "2023-05-21T15:25:31"
        }

        # When:
        response = self.c.get(reverse('payment:point_approve', args=[order.id]), data=data)
        content = json.loads(response.content)

        # Then: 주문 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content['message'],
            '결제가 완료되었습니다.'
        )

    @patch('payment.views.KakaoPay.approve_payment')
    def test_kakao_pay_approve_for_buy_point_api_when_fail_due_order_give_coupon_not_exists(self, mock_approve_payment):
        # Given:
        self.login()
        data = {
            'pg_token': 'test_token',
        }
        # And: OrderGivePoint 제거
        OrderGivePoint.objects.all().delete()
        # And: 주문 생성
        order = Order.objects.create(
            user_id=self.c.user.id,
            product_type=ProductType.POINT.value,
            tid='T469b847306d7b2dc394',
            total_price=1000,
            total_product_price=1000,
            total_user_paid_price=1000,
            total_discount_price=0,
            total_product_discount_price=0,
            status=OrderStatus.READY.value,
            payment=PaymentType.KAKAOPAY.value,
        )
        # And: 모킹
        mock_approve_payment.return_value = {
            "aid": "A469b85a306d7b2dc395",
            "tid": "T469b847306d7b2dc394",
            "cid": "TC0ONETIME",
            "partner_order_id": "test1",
            "partner_user_id": "1",
            "payment_method_type": "MONEY",
            "item_name": "1000 포인트",
            "item_code": "",
            "quantity": 1,
            "amount": {
                "total": 1000,
                "tax_free": 0,
                "vat": 91,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "created_at": "2023-05-21T15:20:55",
            "approved_at": "2023-05-21T15:25:31"
        }

        # When:
        response = self.c.get(reverse('payment:point_approve', args=[order.id]), data=data)
        content = json.loads(response.content)

        # Then: OrderGivePoint 없어서 주문 실패
        self.assertEqual(response.status_code, OrderNotExists.status_code)
        self.assertEqual(content['message'], OrderNotExists.default_detail)

    def test_kakao_pay_approve_for_buy_point_api_when_fail_due_order_not_exists(self):
        # Given:
        self.login()
        data = {
            'pg_token': 'test_token',
        }

        # When: 없는 주문 id 로 결제 신청
        response = self.c.get(reverse('payment:point_approve', args=[99999]), data=data)
        content = json.loads(response.content)

        # Then: Order가 없어서 주문 실패
        self.assertEqual(response.status_code, OrderNotExists.status_code)
        self.assertEqual(content['message'], OrderNotExists.default_detail)


@freeze_time('2021-01-01')
class KakaoPayCancelForBuyPointAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(KakaoPayCancelForBuyPointAPIViewTestCase, self).setUp()
        self.point_product_1000 = PointProduct.objects.create(
            title='1000 포인트 상품',
            description='1000 포인트 상품입니다.',
            price=1000,
            point=1000,
            is_active=True,
            start_time=datetime(2021, 1, 1),
            end_time=datetime(2021, 12, 31),
            quantity=100,
        )

    def test_kakao_pay_cancel_for_buy_point_api_when_success(self):
        # Given:
        self.login()
        # And: 주문 생성
        order = Order.objects.create(
            user_id=self.c.user.id,
            product_type=ProductType.POINT.value,
            tid='T469b847306d7b2dc394',
            total_price=1000,
            total_product_price=1000,
            total_user_paid_price=1000,
            total_discount_price=0,
            total_product_discount_price=0,
            status=OrderStatus.READY.value,
            payment=PaymentType.KAKAOPAY.value,
        )
        # And: OrderGivePoint 생성
        OrderGivePoint.objects.create(
            order_id=order.id,
            user_id=self.c.user.id,
            status=PointGivenStatus.READY.value,
            point=1000,
        )
        # When:
        response = self.c.get(reverse('payment:point_cancel', args=[order.id]))
        content = json.loads(response.content)

        # Then: 주문 취소 성공
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content['message'],
            '결제가 취소되었습니다.'
        )

    def test_kakao_pay_cancel_for_buy_point_api_when_fail_due_order_give_coupon_not_exists(self):
        # Given:
        self.login()
        # And: OrderGivePoint 제거
        OrderGivePoint.objects.all().delete()
        # And: 주문 생성
        order = Order.objects.create(
            user_id=self.c.user.id,
            product_type=ProductType.POINT.value,
            tid='T469b847306d7b2dc394',
            total_price=1000,
            total_product_price=1000,
            total_user_paid_price=1000,
            total_discount_price=0,
            total_product_discount_price=0,
            status=OrderStatus.READY.value,
            payment=PaymentType.KAKAOPAY.value,
        )

        # When:
        response = self.c.get(reverse('payment:point_cancel', args=[order.id]))
        content = json.loads(response.content)

        # Then: OrderGivePoint 없어서 주문 취소 실패
        self.assertEqual(response.status_code, OrderNotExists.status_code)
        self.assertEqual(content['message'], OrderNotExists.default_detail)

    def test_kakao_pay_cancel_for_buy_point_api_when_fail_due_order_not_exists(self):
        # Given:
        self.login()

        # When: 없는 주문 id 로 결제 신청
        response = self.c.get(reverse('payment:point_cancel', args=[99999]))
        content = json.loads(response.content)

        # Then: Order가 없어서 주문 취소 실패
        self.assertEqual(response.status_code, OrderNotExists.status_code)
        self.assertEqual(content['message'], OrderNotExists.default_detail)


@freeze_time('2021-01-01')
class KakaoPayFailForBuyPointAPIViewTestCase(LoginMixin, TestCase):
    def setUp(self):
        super(KakaoPayFailForBuyPointAPIViewTestCase, self).setUp()
        self.point_product_1000 = PointProduct.objects.create(
            title='1000 포인트 상품',
            description='1000 포인트 상품입니다.',
            price=1000,
            point=1000,
            is_active=True,
            start_time=datetime(2021, 1, 1),
            end_time=datetime(2021, 12, 31),
            quantity=100,
        )

    def test_kakao_pay_fail_for_buy_point_api_when_success(self):
        # Given:
        self.login()
        # And: 주문 생성
        order = Order.objects.create(
            user_id=self.c.user.id,
            product_type=ProductType.POINT.value,
            tid='T469b847306d7b2dc394',
            total_price=1000,
            total_product_price=1000,
            total_user_paid_price=1000,
            total_discount_price=0,
            total_product_discount_price=0,
            status=OrderStatus.READY.value,
            payment=PaymentType.KAKAOPAY.value,
        )
        # And: OrderGivePoint 생성
        OrderGivePoint.objects.create(
            order_id=order.id,
            user_id=self.c.user.id,
            status=PointGivenStatus.READY.value,
            point=1000,
        )
        # When:
        response = self.c.get(reverse('payment:point_fail', args=[order.id]))
        content = json.loads(response.content)

        # Then: 주문 실패
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            content['message'],
            '결제가 실패되었습니다.'
        )

    def test_kakao_pay_fail_for_buy_point_api_when_fail_due_order_give_coupon_not_exists(self):
        # Given:
        self.login()
        # And: OrderGivePoint 제거
        OrderGivePoint.objects.all().delete()
        # And: 주문 생성
        order = Order.objects.create(
            user_id=self.c.user.id,
            product_type=ProductType.POINT.value,
            tid='T469b847306d7b2dc394',
            total_price=1000,
            total_product_price=1000,
            total_user_paid_price=1000,
            total_discount_price=0,
            total_product_discount_price=0,
            status=OrderStatus.READY.value,
            payment=PaymentType.KAKAOPAY.value,
        )

        # When:
        response = self.c.get(reverse('payment:point_fail', args=[order.id]))
        content = json.loads(response.content)

        # Then: OrderGivePoint 없어서 주문 실패 실패
        self.assertEqual(response.status_code, OrderNotExists.status_code)
        self.assertEqual(content['message'], OrderNotExists.default_detail)

    def test_kakao_pay_fail_for_buy_point_api_when_fail_due_order_not_exists(self):
        # Given:
        self.login()

        # When: 없는 주문 id 로 결제 신청
        response = self.c.get(reverse('payment:point_fail', args=[99999]))
        content = json.loads(response.content)

        # Then: Order가 없어서 주문 실패 실패
        self.assertEqual(response.status_code, OrderNotExists.status_code)
        self.assertEqual(content['message'], OrderNotExists.default_detail)
