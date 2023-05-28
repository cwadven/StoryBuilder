from django.test import TestCase
from django.utils import timezone

from payment.consts import ProductType
from payment.dtos import PointProductItemDTO
from payment.models import PointProduct, AdditionalPointProduct


class PointProductItemDTOTestCase(TestCase):
    def setUp(self):
        self.active_product = PointProduct.objects.create(
            title='Active Product',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            quantity=10,
            point=2000,
        )
        self.active_additional_product = AdditionalPointProduct.objects.create(
            point_product=self.active_product,
            description='Active Product',
            price=1000,
            start_time=timezone.now() - timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            point=1000,
        )

    def test_point_product_item_dto_when_additional_point_product_exists(self):
        # Given:
        # When:
        point_product_item_dto = PointProductItemDTO.of(self.active_product)

        # Then: product
        self.assertEquals(point_product_item_dto.product_id, self.active_product.id)
        self.assertEquals(point_product_item_dto.product_type, ProductType.POINT.value)
        self.assertEquals(point_product_item_dto.title, self.active_product.title)
        self.assertEquals(point_product_item_dto.description, self.active_product.description)
        self.assertEquals(point_product_item_dto.image, self.active_product.image)
        self.assertEquals(
            point_product_item_dto.total_price,
            self.active_product.price + self.active_additional_product.price,
        )
        self.assertEquals(point_product_item_dto.price, self.active_product.price)
        self.assertEquals(
            point_product_item_dto.total_point,
            self.active_product.point + + self.active_additional_product.point,
        )
        self.assertEquals(point_product_item_dto.point, self.active_product.point)
        self.assertEquals(point_product_item_dto.is_sold_out, self.active_product.is_sold_out)
        self.assertEquals(point_product_item_dto.bought_count, self.active_product.bought_count)
        self.assertEquals(point_product_item_dto.review_count, self.active_product.review_count)
        self.assertEquals(point_product_item_dto.review_rate, self.active_product.review_rate)
        # And: additional_product
        self.assertEquals(
            point_product_item_dto.additional_products[0].point,
            self.active_additional_product.point,
        )
        self.assertEquals(
            point_product_item_dto.additional_products[0].price,
            self.active_additional_product.price,
        )
        self.assertEquals(
            point_product_item_dto.additional_products[0].description,
            self.active_additional_product.description,
        )
