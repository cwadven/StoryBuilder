from django.db.models import Manager, Q
from django.utils import timezone


class ProductManager(Manager):
    def get_actives(self, now=None):
        if now is None:
            now = timezone.now()

        return self.filter(
            (Q(start_time__lte=now) | Q(start_time__isnull=True)),
            (Q(end_time__gte=now) | Q(end_time__isnull=True)),
            is_active=True,
            quantity__gt=0,
            is_sold_out=False,
        )


class AdditionalProductManager(Manager):
    def get_actives(self, now=None):
        if now is None:
            now = timezone.now()

        return self.filter(
            (Q(start_time__lte=now) | Q(start_time__isnull=True)),
            (Q(end_time__gte=now) | Q(end_time__isnull=True)),
            is_active=True,
        )
