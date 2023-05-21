from django.db import models


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
