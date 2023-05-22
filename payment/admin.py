from django.contrib import admin

from payment.admin_forms import PointProductAdminForm
from payment.models import PointProduct, Order


class PointProductAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'description',
        'amount',
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
        'product_id',
        'product_type',
        'tid',
        'total_price',
        'product_price',
        'total_discount_price',
        'product_discount_price',
        'refund_price',
        'status',
        'success_time',
        'refund_time',
    ]
    form = PointProductAdminForm


admin.site.register(PointProduct, PointProductAdmin)
admin.site.register(Order, OrderAdmin)
