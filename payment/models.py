from django.db import models

from payment.consts import OrderStatus, ProductType


class Order(models.Model):
    """
    tid 없을 수 있습니다.
    total_actual_price: 제품 금액, 수수류, 배달비 등
    total_discount_price: 쿠폰, 포인트 등
    total_user_paid_price: 사용자 결제한 금액
    """
    user_id = models.BigIntegerField(verbose_name='User ID', db_index=True)
    product_id = models.BigIntegerField(verbose_name='상품 ID', db_index=True)
    product_type = models.CharField(verbose_name='상품 타입', max_length=20, db_index=True, choices=ProductType.choices())
    tid = models.CharField(verbose_name='결제 고유 번호', max_length=50, db_index=True, null=True, blank=True)
    total_price = models.IntegerField(verbose_name='총 결제 금액', default=0, db_index=True)
    total_product_price = models.IntegerField(verbose_name='제품 결제 금액', default=0, db_index=True)
    total_user_paid_price = models.IntegerField(verbose_name='사용자 결제 금액', default=0, db_index=True)
    total_discount_price = models.IntegerField(verbose_name='총 할인 금액', default=0, db_index=True)
    total_product_discount_price = models.IntegerField(verbose_name='제품 할인 금액', default=0, db_index=True)
    total_refund_price = models.IntegerField(verbose_name='환불 금액', default=0, db_index=True)
    status = models.CharField(verbose_name='결제 상태', max_length=20, db_index=True, choices=OrderStatus.choices())
    payment = models.CharField(verbose_name='결제 수단', max_length=20, db_index=True)
    user_notification_sent = models.BooleanField(verbose_name='고객 알림 전송 여부', default=False)
    success_time = models.DateTimeField(verbose_name='결제 성공 시간', null=True, blank=True, db_index=True)
    has_refund = models.BooleanField(verbose_name='환불 여부', default=False)
    refund_time = models.DateTimeField(verbose_name='환불 시간', null=True, blank=True, db_index=True)
    request_time = models.DateTimeField(verbose_name='생성일', auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='주문', on_delete=models.CASCADE, related_name='items')
    user_id = models.BigIntegerField(verbose_name='User ID', db_index=True)
    product_id = models.BigIntegerField(verbose_name='상품 ID', db_index=True)
    product_type = models.CharField(verbose_name='상품 타입', max_length=20, db_index=True, choices=ProductType.choices())
    product_price = models.IntegerField(verbose_name='제품 결제 금액', default=0, db_index=True)
    discount_price = models.IntegerField(verbose_name='총 할인 금액', default=0, db_index=True)
    user_paid_price = models.IntegerField(verbose_name='사용자 결제 금액', default=0, db_index=True)
    refund_price = models.IntegerField(verbose_name='환불 금액', default=0, db_index=True)
    item_quantity = models.IntegerField(verbose_name='제품 수량', default=0, db_index=True)
    status = models.CharField(verbose_name='결제 상태', max_length=20, db_index=True, choices=OrderStatus.choices())
    success_time = models.DateTimeField(verbose_name='결제 성공 시간', null=True, blank=True, db_index=True)
    refund_time = models.DateTimeField(verbose_name='환불 시간', null=True, blank=True, db_index=True)
    request_time = models.DateTimeField(verbose_name='생성일', auto_now_add=True)


class Product(models.Model):
    title = models.CharField(verbose_name='상품명', max_length=120, db_index=True)
    description = models.TextField(verbose_name='상품 설명', null=True, blank=True)
    image = models.TextField(verbose_name='상품 이미지', null=True, blank=True)
    amount = models.IntegerField(verbose_name='가격 정보', db_index=True)
    is_active = models.BooleanField(verbose_name='활성화', default=True, db_index=True)
    start_time = models.DateTimeField(verbose_name='시작 시간', null=True, blank=True, db_index=True)
    end_time = models.DateTimeField(verbose_name='끝 시간', null=True, blank=True, db_index=True)
    quantity = models.IntegerField(verbose_name='수량', default=0, db_index=True)
    is_sold_out = models.BooleanField(verbose_name='품절 여부', default=False, db_index=True)
    bought_count = models.BigIntegerField(verbose_name='구매 수', default=0, db_index=True)
    review_count = models.BigIntegerField(verbose_name='리뷰 수', default=0, db_index=True)
    review_rate = models.FloatField(verbose_name='리뷰 평점', default=0, db_index=True)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.title} - {self.amount}'


class PointProduct(Product):
    point = models.IntegerField(verbose_name='포인트', db_index=True)

    def __str__(self):
        return f'{self.title} - {self.amount} - {self.point}'


class AdditionalPointProduct(models.Model):
    point_product = models.ForeignKey(PointProduct, on_delete=models.CASCADE)
    description = models.CharField(verbose_name='추가 포인트 주는 이유', max_length=120)
    point = models.IntegerField(verbose_name='추가 포인트')
    start_time = models.DateTimeField(verbose_name='유효한 시작 시간', null=True, blank=True, db_index=True)
    end_time = models.DateTimeField(verbose_name='유효한 끝 시간', null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)


# class Product(models.Model):
#     title = models.CharField(verbose_name='상품명', max_length=120, db_index=True)
#     description = models.TextField(verbose_name='상품 설명', null=True, blank=True)
#     image = models.TextField(verbose_name='상품 이미지', null=True, blank=True)
#     amount = models.IntegerField(verbose_name='가격 정보', db_index=True)
#     is_active = models.BooleanField(verbose_name='유효성', default=True, db_index=True)
#     start_time = models.DateTimeField(verbose_name='시작 시간', null=True, blank=True, db_index=True)
#     end_time = models.DateTimeField(verbose_name='끝 시간', null=True, blank=True, db_index=True)
#     quantity = models.IntegerField(verbose_name='수량', default=0, db_index=True)
#     is_sold_out = models.BooleanField(verbose_name='품절 여부', default=False, db_index=True)
#     bought_count = models.BigIntegerField(verbose_name='구매 수', default=0, db_index=True)
#     review_count = models.BigIntegerField(verbose_name='리뷰 수', default=0, db_index=True)
#     review_rate = models.FloatField(verbose_name='리뷰 평점', default=0, db_index=True)
#     created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
#     updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)
#
#     def __str__(self):
#         return f'{self.title} - {self.amount}'
#
#
# class ProductDescription(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     html = models.TextField(verbose_name='html', null=True, blank=True)
#     image = models.TextField(verbose_name='이미지', null=True, blank=True)
#     image_redirect_url = models.TextField(verbose_name='리다이렉트 url', null=True, blank=True)
#     sequence = models.PositiveIntegerField(verbose_name='순서', db_index=True)
#     created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
#     updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)
#
#     def __str__(self):
#         return f'{self.id} - {self.product_id}'
