from django.db.models import Manager
from django.utils import timezone


class ProductManager(Manager):
    def get_actives(self, now=None):
        if now is None:
            now = timezone.now()

        return self.filter(
            is_active=True,
            start_time__lte=now,
            end_time__gte=now,
            quantity__gt=0,
            is_sold_out=False,
        )
