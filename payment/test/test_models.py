from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time

from account.models import User
from payment.consts import PaymentType, OrderStatus, ProductType, PointGivenStatus
from payment.models import PointProduct, Order, AdditionalPointProduct, OrderItem, OrderGivePoint
from point.models import UserPoint


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
        order = self.point_product_1000.create_order(self.user.id, PaymentType.KAKAOPAY_CARD.value, quantity)

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
        # And: OrderGivePoint 생성
        order_give_point = OrderGivePoint.objects.get(order_id=order.id)
        self.assertEqual(order_give_point.user_id, self.user.id)
        self.assertEqual(order_give_point.point, self.point_product_1000.point * quantity)

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
        order = self.point_product_1000.create_order(self.user.id, PaymentType.KAKAOPAY_CARD.value, quantity)

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
        # And: OrderGivePoint 생성
        order_give_point = OrderGivePoint.objects.get(order_id=order.id)
        self.assertEqual(order_give_point.user_id, self.user.id)
        self.assertEqual(
            order_give_point.point,
            self.point_product_1000.point * quantity + additional_point_product.point * quantity
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

    def test_cancel(self):
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
        order.cancel()

        # Then: Order CANCEL 변경
        self.assertTrue(
            Order.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                status=OrderStatus.CANCEL.value,
                payment=PaymentType.KAKAOPAY_CARD.value,
                total_price=(self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_product_price=(
                        self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_user_paid_price=(
                        self.point_product_1000.price * quantity + additional_point_product.price * quantity),
                total_discount_price=0,
                total_product_discount_price=0,
                success_time=None,
            ).exists()
        )
        # And: OrderItem CANCEL 변경
        self.assertTrue(
            OrderItem.objects.filter(
                user_id=self.user.id,
                product_type=ProductType.POINT.value,
                product_id=self.point_product_1000.id,
                product_price=self.point_product_1000.price * quantity,
                discount_price=0,
                user_paid_price=self.point_product_1000.price * quantity,
                item_quantity=quantity,
                status=OrderStatus.CANCEL.value,
                success_time=None,
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
                status=OrderStatus.CANCEL.value,
                success_time=None,
            ).exists()
        )


@freeze_time('2022-01-01')
class OrderGivePointMethodTestCase(TestCase):
    def setUp(self):
        pass

    def test_ready(self):
        # Given:
        order_id = 1
        user_id = 1
        point = 1000

        # When:
        order_give_point = OrderGivePoint.ready(order_id, user_id, point)

        # Then:
        self.assertEqual(order_give_point.order_id, order_id)
        self.assertEqual(order_give_point.user_id, user_id)
        self.assertEqual(order_give_point.point, point)
        self.assertEqual(order_give_point.status, PointGivenStatus.READY.value)

    def test_give(self):
        # Given: OrderGivePoint 생성
        order_id = 1
        user_id = 1
        point = 1000
        order_give_point = OrderGivePoint.ready(order_id, user_id, point)

        # When: give
        order_give_point.give()

        # Then: OrderGivePoint SUCCESS 변경
        order_give_point = OrderGivePoint.objects.get(id=order_give_point.id)
        self.assertEqual(order_give_point.status, PointGivenStatus.SUCCESS.value)
        self.assertEqual(order_give_point.updated_at, datetime(2022, 1, 1))
        # And: UserPoint 생성
        self.assertTrue(
            UserPoint.objects.filter(
                user_id=user_id,
                point=point,
                description='포인트 구매',
            ).exists()
        )

    def test_cancel(self):
        # Given: OrderGivePoint 생성
        order_id = 1
        user_id = 1
        point = 1000
        order_give_point = OrderGivePoint.ready(order_id, user_id, point)

        # When: cancel
        order_give_point.cancel()

        # Then: OrderGivePoint CANCEL 변경
        order_give_point = OrderGivePoint.objects.get(id=order_give_point.id)
        self.assertEqual(order_give_point.status, PointGivenStatus.CANCEL.value)
        self.assertEqual(order_give_point.updated_at, datetime(2022, 1, 1))
        # And: UserPoint 생성 안됨
        self.assertFalse(
            UserPoint.objects.filter(
                user_id=user_id,
                point=point,
                description='포인트 구매',
            ).exists()
        )
