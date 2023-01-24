from django.db import models

from account.models import User


class UserPoint(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    point = models.IntegerField(verbose_name='포인트')
    description = models.CharField(verbose_name='생성된 이유', max_length=120)
    is_active = models.BooleanField(verbose_name='유효성', default=True, db_index=True)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)
