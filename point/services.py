from django.db.models import Sum
from django.db.models.functions import Coalesce

from config.common.exception_codes import NotEnoughUserPoints
from point.models import UserPoint


def get_user_available_total_point(user_id: int) -> int:
    total_point = UserPoint.objects.filter(
        user_id=user_id,
        is_active=True
    ).aggregate(
        total_point=Coalesce(Sum('point'), 0)
    ).get(
        'total_point'
    )
    return max(total_point, 0)


def use_point(user_id: int, point: int, description: str):
    total_point = get_user_available_total_point(user_id)
    if total_point < point:
        raise NotEnoughUserPoints
    return UserPoint.objects.create(
        user_id=user_id,
        point=-point,
        description=description,
    )


def give_point(user_id: int, point: int, description: str):
    return UserPoint.objects.create(
        user_id=user_id,
        point=point,
        description=description,
    )
