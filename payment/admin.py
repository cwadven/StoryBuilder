from django.contrib import admin

from payment.admin_forms import PointProductAdminForm
from payment.models import PointProduct, Order


class PointProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'description',
        'price',
        'is_active',
        'start_time',
        'end_time',
        'quantity',
        'is_sold_out',
        'point',
    ]
    form = PointProductAdminForm


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_id',
        'product_type',
        'tid',
        'total_price',
        'total_product_price',
        'total_user_paid_price',
        'total_discount_price',
        'total_product_discount_price',
        'total_refund_price',
        'status',
        'payment',
        'success_time',
        'has_refund',
        'refund_time',
    ]


admin.site.register(PointProduct, PointProductAdmin)
admin.site.register(Order, OrderAdmin)
