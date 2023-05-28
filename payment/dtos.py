import attr
from typing import List

from django.db.models import Sum

from payment.consts import ProductType
from payment.models import PointProduct


@attr.s
class PointPayReadyRequestDTO(object):
    product_id = attr.ib(type=int)
    partner_order_id = attr.ib(type=str)
    partner_user_id = attr.ib(type=str)
    item_name = attr.ib(type=str)
    cid_secret = attr.ib(type=str, default=None)

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class KakaoPayReadyResponseDTO(object):
    tid = attr.ib(type=str)
    next_redirect_mobile_url = attr.ib(type=str)

    @classmethod
    def from_dict(cls, data):
        return cls(
            tid=data['tid'],
            next_redirect_mobile_url=data['next_redirect_mobile_url'],
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class AdditionalPointProductItemDTO(object):
    description = attr.ib(type=str)
    price = attr.ib(type=str)
    point = attr.ib(type=str)

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class PointProductItemDTO(object):
    product_id = attr.ib(type=int)
    product_type = attr.ib(type=str)
    title = attr.ib(type=str)
    description = attr.ib(type=str)
    image = attr.ib(type=str)
    total_price = attr.ib(type=int)
    price = attr.ib(type=int)
    total_point = attr.ib(type=int)
    point = attr.ib(type=int)
    is_sold_out = attr.ib(type=bool)
    bought_count = attr.ib(type=int)
    review_count = attr.ib(type=int)
    review_rate = attr.ib(type=float)
    additional_products = attr.ib(type=List[AdditionalPointProductItemDTO])

    @classmethod
    def of(cls, point_product: PointProduct) -> 'PointProductItemDTO':
        additional_products = []
        total_price = point_product.price
        total_point = point_product.price
        for additional_product in point_product.additionalpointproduct_set.get_actives():
            total_price += additional_product.price
            total_point += additional_product.point
            additional_products.append(
                AdditionalPointProductItemDTO(
                    description=additional_product.description,
                    price=additional_product.price,
                    point=additional_product.point,
                )
            )
        return cls(
            product_id=point_product.id,
            product_type=ProductType.POINT.value,
            title=point_product.title,
            description=point_product.description,
            image=point_product.image,
            total_price=total_price,
            price=point_product.price,
            total_point=total_point,
            point=point_product.point,
            is_sold_out=point_product.is_sold_out,
            bought_count=point_product.bought_count,
            review_count=point_product.review_count,
            review_rate=point_product.review_rate,
            additional_products=additional_products,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)
