from datetime import datetime

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
    version = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.id} {self.answer}'

    class Meta:
        verbose_name = 'Sheet 정답 데이터'
        verbose_name_plural = 'Sheet 정답 데이터'


class NextSheetPath(models.Model):
    answer = models.ForeignKey(SheetAnswer, on_delete=models.CASCADE, verbose_name='정답')
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE, verbose_name='정답을 맞춘 후, 다음 시트')
    quantity = models.IntegerField(verbose_name='가중치', default=1)

    def __str__(self):
        return f'{self.id} {self.sheet_id} {self.answer_id} {self.quantity}'
    
    class Meta:
        verbose_name = '정답에 의한 다음 Sheet 경로'
        verbose_name_plural = '정답에 의한 다음 Sheet 경로'


class UserSheetAnswerSolve(models.Model):
    """
    story: 사용자가 풀고 있는 스토리
    user_story_solve: 사용자가 풀고 있는 스토리에 관한 풀었던 정보
    sheet: 현재 sheet
    next_sheet_path: 문제를 풀었으면 풀었던 내용의 다음 시트
    sheet_question: 현재 sheet 의 문제 Snapshot 으로 나중에 문제가 바꿔졌을 경우 히스토리성으로 가지고 있을 필요
    answer: 사용자가 맞춘 현재 sheet 의 정답 Snapshot 으로 나중에 정답이 바꿔졌을 경우 히스토리성으로 가지고 있을 필요
    solved_sheet_version: 풀었던 sheet 의 버전
    solved_answer_version: 풀었던 정답의 버전
    solving_status: 현재 문제를 풀고 있는 중인지 혹은 성공했는지 확인용
    start_time: 문제를 푼 시간
    solved_time: 문제를 해결한 시간
    """
    SOLVING_STATUS_CHOICES = (
        ('solving', '진행중'),
        ('solved', '성공'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True)
    user_story_solve = models.ForeignKey(UserStorySolve, on_delete=models.SET_NULL, null=True)
    sheet = models.ForeignKey(Sheet, on_delete=models.SET_NULL, null=True)
    next_sheet_path = models.ForeignKey(NextSheetPath, on_delete=models.SET_NULL, null=True)
    sheet_question = models.TextField(null=True)
    answer = models.TextField(null=True)
    solved_sheet_version = models.IntegerField(null=True)
    solved_answer_version = models.IntegerField(null=True)
    solving_status = models.CharField(
        max_length=20,
        choices=SOLVING_STATUS_CHOICES,
        default=SOLVING_STATUS_CHOICES[0][0],
        db_index=True,
    )
    start_time = models.DateTimeField(null=True)
    solved_time = models.DateTimeField(null=True)

    @classmethod
    def generate_cls_if_first_time(cls, user, sheet_id):
        try:
            sheet = Sheet.objects.select_related(
                'story',
            ).get(
                id=sheet_id
            )
            user_story_solve = UserStorySolve.objects.get(
                user_id=user.id,
                story=sheet.story
            )
            user_sheet_answer_solve, is_created = cls.objects.get_or_create(
                user=user,
                story=sheet.story,
                user_story_solve=user_story_solve,
                sheet=sheet,
            )
            user_sheet_answer_solve.start_time = datetime.now()
            user_sheet_answer_solve.save(update_fields=['start_time'])
        except (Sheet.DoesNotExist, UserStorySolve.DoesNotExist):
            return None, None
        return user_sheet_answer_solve, is_created

    def solved_sheet_action(self, answer, sheet_question, solved_sheet_version, solved_answer_version, next_sheet_path):
        self.answer = answer
        self.sheet_question = sheet_question
        self.solved_sheet_version = solved_sheet_version
        self.solved_answer_version = solved_answer_version
        self.next_sheet_path = next_sheet_path
        self.solving_status = self.SOLVING_STATUS_CHOICES[1][0]
        self.solved_time = datetime.now()
        self.save(
            update_fields=[
                'solving_status',
                'solved_time',
                'answer',
                'solved_sheet_version',
                'solved_answer_version',
                'next_sheet_path',
            ]
        )
