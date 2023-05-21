from django.contrib import admin

from payment.admin_forms import PointProductAdminForm
from payment.models import PointProduct


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


admin.site.register(PointProduct, PointProductAdmin)
