from datetime import datetime

from typing import List

from django.db.models import QuerySet

from banner.models import Banner
from config.common.exception_codes import BannerDoesNotExists


def get_active_banners(now=None, order_by: List[str] = None) -> QuerySet[Banner]:
    if now is None:
        now = datetime.now()

    banner_qs = Banner.objects.get_activate(now=now)
    if order_by:
        banner_qs = banner_qs.order_by(*order_by)

    return banner_qs


def get_active_banner(banner_id: int, now=None) -> Banner:
    if now is None:
        now = datetime.now()

    try:
        return get_active_banners(now=now).get(id=banner_id)
    except Banner.DoesNotExist:
        raise BannerDoesNotExists()
