from django.db import models

from account.models import User


class Story(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(verbose_name='제목', max_length=100)
    description = models.TextField(verbose_name='설명', blank=True, null=True)
    image = models.TextField(verbose_name='대표 이미지', blank=True, null=True)
    background_image = models.TextField(verbose_name='대표 배경 이미지', blank=True, null=True)
    played_count = models.IntegerField(verbose_name='플레이 횟수', default=0)
    view_count = models.IntegerField(verbose_name='조회 횟수', default=0)
    review_rate = models.IntegerField(verbose_name='평점', default=0)
    is_deleted = models.BooleanField(verbose_name='삭제 여부', default=False)
    displayable = models.BooleanField(verbose_name='활성화 여부', default=True)
    playing_point = models.IntegerField(verbose_name='플레이를 위한 포인트', default=0)
    need_to_pay = models.BooleanField(verbose_name='구매 여부', default=False)
    free_to_play_sheet_count = models.IntegerField(verbose_name='무료로 즐길 수 있는 Sheet 갯수', default=0)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)

    def __str__(self):
        return f'{self.id} {self.title}'


class UserStorySolve(models.Model):
    STATUS_CHOICES = (
        ('solving', '진행중'),
        ('give_up', '포기'),
        ('solved', '성공'),
    )
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    solved_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'User: {self.user_id} Story: {self.story_id} Status: {self.status}'


class Sheet(models.Model):
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True)
    title = models.CharField(verbose_name='제목', max_length=100)
    question = models.TextField(verbose_name='질문')
    image = models.TextField(verbose_name='대표 이미지', blank=True, null=True)
    background_image = models.TextField(verbose_name='대표 배경 이미지', blank=True, null=True)
    is_deleted = models.BooleanField(verbose_name='삭제 여부', default=False)
    version = models.IntegerField(verbose_name='수정 시 자동 변경 되는 버전', default=0)
    is_start = models.BooleanField(verbose_name='시작 부분 여부', default=False)
    is_final = models.BooleanField(verbose_name='마지막 부분 여부', default=False)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)

    def __str__(self):
        return f'{self.id} {self.title}'


class SheetAnswer(models.Model):
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE, null=True)
    answer = models.TextField(verbose_name='정답')
    answer_reply = models.TextField(verbose_name='정답 후 반응', blank=True, null=True)
    next_sheet_paths = models.ManyToManyField(
        to=Sheet,
        through='NextSheetPath',
        null=True,
        blank=True,
        related_name='next_sheet_paths',
        verbose_name='다음 Sheet 경로'
    )

    def __str__(self):
        return f'{self.id} {self.answer}'


class NextSheetPath(models.Model):
    answer = models.ForeignKey(SheetAnswer, on_delete=models.CASCADE)
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name='가중치', default=1)

    def __str__(self):
        return f'{self.id} {self.sheet_id} {self.answer_id} {self.quantity}'
