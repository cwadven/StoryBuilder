from django.test import TestCase
from django.utils import timezone

from payment.models import PointProduct, AdditionalPointProduct


class TestProductManager(TestCase):
    def setUp(self):
        # Set up data for the test
        self.active_product = PointProduct.objects.create(
            title='Active Product',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            quantity=10,
            point=1000,
        )

        self.inactive_product_future = PointProduct.objects.create(
            title='Inactive Product Future',
            price=1000,
            start_time=timezone.now() + timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=2),
            quantity=10,
            point=1000,
        )

        self.inactive_product_past = PointProduct.objects.create(
            title='Inactive Product Past',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=2),
            end_time=timezone.now() - timezone.timedelta(hours=1),
            quantity=10,
            point=1000,
        )

        self.inactive_product_sold_out = PointProduct.objects.create(
            title='Inactive Product Sold Out',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            quantity=0,
            is_sold_out=True,
            point=1000,
        )

    def test_get_actives(self):
        # Test get_actives method
        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertEqual(active_products.count(), 1)
        self.assertEqual(active_products.first(), self.active_product)

    def test_get_active_products_when_end_date_is_not_exists(self):
        # Given: end_time Null 생성
        self.active_product.end_time = None
        self.active_product.save()

        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertEqual(active_products.count(), 1)
        self.assertEqual(active_products.first(), self.active_product)

    def test_inactive_product_future(self):
        # Check that the product with future start time is not included
        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertNotIn(self.inactive_product_future, active_products)

    def test_inactive_product_past(self):
        # Check that the product with past end time is not included
        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertNotIn(self.inactive_product_past, active_products)

    def test_inactive_product_sold_out(self):
        # Check that the sold out product is not included
        # When: 실행
        active_products = PointProduct.objects.get_actives()

        # Then:
        self.assertNotIn(self.inactive_product_sold_out, active_products)


class TestAdditionalProductManager(TestCase):
    def setUp(self):
        # Set up data for the test
        self.active_product = PointProduct.objects.create(
            title='Active Product',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            quantity=10,
            point=1000,
        )

        self.active_additional_product = AdditionalPointProduct.objects.create(
            point_product=self.active_product,
            description='Active Product',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            point=1000,
        )

        self.inactive_additional_product_future = AdditionalPointProduct.objects.create(
            point_product=self.active_product,
            description='Inactive Product Future',
            price=1000,
            start_time=timezone.now() + timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=2),
            point=1000,
        )

        self.inactive_additional_product_past = AdditionalPointProduct.objects.create(
            point_product=self.active_product,
            description='Inactive Product Past',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=2),
            end_time=timezone.now() - timezone.timedelta(hours=1),
            point=1000,
        )

        self.inactive_additional_product_is_not_active = AdditionalPointProduct.objects.create(
            point_product=self.active_product,
            description='Inactive Product deactivate',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            is_active=False,
            point=1000,
        )

    def test_get_actives(self):
        # Test get_actives method
        # When: 실행
        active_additional_products = AdditionalPointProduct.objects.get_actives()

        # Then:
        self.assertEqual(active_additional_products.count(), 1)
        self.assertEqual(active_additional_products.first(), self.active_additional_product)

    def test_inactive_product_future(self):
        # Check that the product with future start time is not included
        # When: 실행
        additional_products = AdditionalPointProduct.objects.get_actives()

        # Then:
        self.assertNotIn(self.inactive_additional_product_future, additional_products)

    def test_inactive_product_past(self):
        # Check that the product with past end time is not included
        # When: 실행
        additional_products = AdditionalPointProduct.objects.get_actives()

        # Then:
        self.assertNotIn(self.inactive_additional_product_past, additional_products)

    def test_inactive_product_is_not_active(self):
        # Check that the sold out product is not included
        # When: 실행
        additional_products = AdditionalPointProduct.objects.get_actives()

        # Then:
        self.assertNotIn(self.inactive_additional_product_is_not_active, additional_products)
