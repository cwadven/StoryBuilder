from datetime import datetime

from django.db.models import Manager, Q


class BannerManager(Manager):
    def get_activate(self, now=None):
        if not now:
            now = datetime.now()

        return self.select_related(
            'banner_type',
        ).filter(
            Q(end_time__gte=now) | Q(end_time__isnull=True),
            is_active=True,
        )
