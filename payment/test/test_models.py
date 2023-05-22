from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time

from account.models import User
from payment.consts import PaymentType, OrderStatus, ProductType
from payment.models import PointProduct, Order, AdditionalPointProduct, OrderItem


@freeze_time('2022-01-01')
class PointProductMethodTestCase(TestCase):
    def setUp(self):
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
        self.user = User.objects.all()[0]

    def test_point_product_create_order_when_not_additional_point_exists(self):
        # Given:
        quantity = 2

        # When: create_order 실행
        self.point_product_1000.create_order(self.user.id, PaymentType.KAKAOPAY_CARD.value, quantity)

        # Then: Order 주문 생성
        self.assertTrue(
            Order.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                status=OrderStatus.READY.value,
                payment=PaymentType.KAKAOPAY_CARD.value,
                total_price=self.point_product_1000.price * quantity,
                total_product_price=self.point_product_1000.price * quantity,
                total_user_paid_price=self.point_product_1000.price * quantity,
                total_discount_price=0,
                total_product_discount_price=0,
            ).exists()
        )
        # And: OrderItem 생성
        self.assertTrue(
            OrderItem.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                product_id=self.point_product_1000.id,
                product_price=self.point_product_1000.price * quantity,
                discount_price=0,
                user_paid_price=self.point_product_1000.price * quantity,
                item_quantity=quantity,
                status=OrderStatus.READY.value,
            ).exists()
        )

    def test_point_product_create_order_when_additional_point_exists(self):
        # Given: AdditionalPointProduct 생성
        quantity = 2
        additional_point_product = AdditionalPointProduct.objects.create(
            point_product=self.point_product_1000,
            description='추가 세일 상품',
            price=250,
            point=500,
            is_active=True,
            start_time=datetime(2021, 1, 1),
            end_time=datetime(2021, 12, 31),
        )

        # When: create_order 실행
        self.point_product_1000.create_order(self.user.id, PaymentType.KAKAOPAY_CARD.value, quantity)

        # Then: Order 주문 생성
        self.assertTrue(
            Order.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                status=OrderStatus.READY.value,
                payment=PaymentType.KAKAOPAY_CARD.value,
                total_price=(self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_product_price=(self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_user_paid_price=(self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_discount_price=0,
                total_product_discount_price=0,
            ).exists()
        )
        # And: OrderItem 생성
        self.assertTrue(
            OrderItem.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                product_id=self.point_product_1000.id,
                product_price=self.point_product_1000.price * quantity,
                discount_price=0,
                user_paid_price=self.point_product_1000.price * quantity,
                item_quantity=quantity,
                status=OrderStatus.READY.value,
            ).exists()
        )
        self.assertTrue(
            OrderItem.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.ADDITIONAL_POINT.value,
                product_id=additional_point_product.id,
                product_price=additional_point_product.price * quantity,
                discount_price=0,
                user_paid_price=additional_point_product.price * quantity,
                item_quantity=quantity,
                status=OrderStatus.READY.value,
            ).exists()
        )


@freeze_time('2022-01-01')
class OrderMethodTestCase(TestCase):
    def setUp(self):
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
        self.user = User.objects.all()[0]

    def test_approved(self):
        # Given: AdditionalPointProduct 생성
        quantity = 2
        additional_point_product = AdditionalPointProduct.objects.create(
            point_product=self.point_product_1000,
            description='추가 세일 상품',
            price=250,
            point=500,
            is_active=True,
            start_time=datetime(2021, 1, 1),
            end_time=datetime(2021, 12, 31),
        )
        # And: 주문 생성
        order = self.point_product_1000.create_order(self.user.id, PaymentType.KAKAOPAY_CARD.value, quantity)
        self.assertTrue(
            Order.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                status=OrderStatus.READY.value,
                payment=PaymentType.KAKAOPAY_CARD.value,
                total_price=(self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_product_price=(
                            self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_user_paid_price=(
                            self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_discount_price=0,
                total_product_discount_price=0,
            ).exists()
        )
        # And: OrderItem 생성
        self.assertTrue(
            OrderItem.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                product_id=self.point_product_1000.id,
                product_price=self.point_product_1000.price * quantity,
                discount_price=0,
                user_paid_price=self.point_product_1000.price * quantity,
                item_quantity=quantity,
                status=OrderStatus.READY.value,
            ).exists()
        )
        self.assertTrue(
            OrderItem.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.ADDITIONAL_POINT.value,
                product_id=additional_point_product.id,
                product_price=additional_point_product.price * quantity,
                discount_price=0,
                user_paid_price=additional_point_product.price * quantity,
                item_quantity=quantity,
                status=OrderStatus.READY.value,
            ).exists()
        )
        # And: order tid 설정
        order.tid = 'test_tid'
        order.save()

        # When: approved
        order.approved(PaymentType.KAKAOPAY_CARD.value)

        # Then: Order SUCCESS 변경
        self.assertTrue(
            Order.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                status=OrderStatus.SUCCESS.value,
                payment=PaymentType.KAKAOPAY_CARD.value,
                total_price=(self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_product_price=(
                        self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_user_paid_price=(
                        self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_discount_price=0,
                total_product_discount_price=0,
                success_time=datetime(2022, 1, 1),
            ).exists()
        )
        # And: OrderItem SUCCESS 변경
        self.assertTrue(
            OrderItem.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                product_id=self.point_product_1000.id,
                product_price=self.point_product_1000.price * quantity,
                discount_price=0,
                user_paid_price=self.point_product_1000.price * quantity,
                item_quantity=quantity,
                status=OrderStatus.SUCCESS.value,
                success_time=datetime(2022, 1, 1),
            ).exists()
        )
        self.assertTrue(
            OrderItem.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.ADDITIONAL_POINT.value,
                product_id=additional_point_product.id,
                product_price=additional_point_product.price * quantity,
                discount_price=0,
                user_paid_price=additional_point_product.price * quantity,
                item_quantity=quantity,
                status=OrderStatus.SUCCESS.value,
                success_time=datetime(2022, 1, 1),
            ).exists()
        )
