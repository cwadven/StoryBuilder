from datetime import datetime

from django.db.models import Manager


class BannerManager(Manager):
    def get_activate(self, now=None):
        if not now:
            now = datetime.now()

        return self.select_related(
            'banner_type',
        ).filter(
            is_active=True,
            end_time__gte=now,
        )
