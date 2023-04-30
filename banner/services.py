from datetime import datetime

from typing import List

from banner.models import Banner


def get_active_banners(now=None, order_by: List[str] = None) -> List[Banner]:
    if now is None:
        now = datetime.now()

    banner_qs = Banner.objects.get_activate(now=now)
    if order_by:
        banner_qs = banner_qs.order_by(*order_by)

    return banner_qs
