from django.test import TestCase
from django.utils import timezone

from payment.models import PointProduct


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
        active_products = PointProduct.objects.get_actives()
        self.assertEqual(active_products.count(), 1)
        self.assertEqual(active_products.first(), self.active_product)

    def test_inactive_product_future(self):
        # Check that the product with future start time is not included
        active_products = PointProduct.objects.get_actives()
        self.assertNotIn(self.inactive_product_future, active_products)

    def test_inactive_product_past(self):
        # Check that the product with past end time is not included
        active_products = PointProduct.objects.get_actives()
        self.assertNotIn(self.inactive_product_past, active_products)

    def test_inactive_product_sold_out(self):
        # Check that the sold out product is not included
        active_products = PointProduct.objects.get_actives()
        self.assertNotIn(self.inactive_product_sold_out, active_products)
