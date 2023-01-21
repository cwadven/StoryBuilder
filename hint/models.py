from django.db import models

from account.models import User
from story.models import Sheet


class SheetHint(models.Model):
    sheet = models.ForeignKey(Sheet, on_delete=models.SET_NULL, null=True)
    hint = models.TextField(verbose_name='힌트 내용', blank=True, null=True)
    image = models.TextField(verbose_name='힌트 이미지', blank=True, null=True)
    sequence = models.IntegerField(null=True, verbose_name='보여주는 순서')
    is_deleted = models.BooleanField(verbose_name='삭제 여부', default=False)
    point = models.IntegerField(verbose_name='힌트를 보기 위한 포인트', default=0)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)

    def __str__(self):
        return f'{self.id} {self.hint}'


class UserSheetHintHistory(models.Model):
    """
    히스토리 가지고 있으면 Sheet Hint 아무 조건 없이 보여줍니다.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sheet_hint = models.ForeignKey(SheetHint, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)

    def __str__(self):
        return f'{self.id}'
