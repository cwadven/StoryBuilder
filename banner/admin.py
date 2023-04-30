from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse

from banner.models import BannerType, Banner


class BannerTypeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'description',
    ]


class BannerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'description',
        'banner_type_name',
        'sequence',
        'start_time',
        'end_time',
        'is_active',
        'status',
    ]

    def get_queryset(self, request):
        return super(BannerAdmin, self).get_queryset(
            request
        ).select_related(
            'banner_type',
        )

    def banner_type_name(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:banner_bannertype_change", args=[obj.banner_type_id]),
            obj.banner_type.name,
        ))
    banner_type_name.short_description = '배너 타입'


admin.site.register(BannerType, BannerTypeAdmin)
admin.site.register(Banner, BannerAdmin)
