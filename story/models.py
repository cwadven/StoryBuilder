from datetime import datetime

from django.contrib.auth.models import AnonymousUser
from django.db import models

from account.models import User
from .constants import StoryLevel
from .managers import StoryManager, PopularStoryManager
from .task import send_user_sheet_solved_email


class Story(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(verbose_name='제목', max_length=100)
    description = models.TextField(verbose_name='설명', blank=True, null=True)
    image = models.TextField(verbose_name='대표 이미지', blank=True, null=True)
    background_image = models.TextField(verbose_name='대표 배경 이미지', blank=True, null=True)
    played_count = models.IntegerField(verbose_name='플레이 횟수', default=0)
    like_count = models.IntegerField(verbose_name='좋아요 횟수', default=0, db_index=True)
    view_count = models.IntegerField(verbose_name='조회 횟수', default=0)
    review_rate = models.IntegerField(verbose_name='평점', default=0)
    is_deleted = models.BooleanField(verbose_name='삭제 여부', default=False)
    displayable = models.BooleanField(verbose_name='활성화 여부', default=True)
    playing_point = models.IntegerField(verbose_name='플레이를 위한 포인트', default=0)
    need_to_pay = models.BooleanField(verbose_name='구매 여부', default=False)
    free_to_play_sheet_count = models.IntegerField(verbose_name='무료로 즐길 수 있는 Sheet 갯수', default=0)
    level = models.IntegerField(
        verbose_name='난이도',
        default=StoryLevel.EASY.value,
        help_text='0: 하, 1: 중, 2: 상, 3: 최상',
    )
    is_secret = models.BooleanField(verbose_name='비밀 여부', default=False, db_index=True)
    secret_members = models.ManyToManyField(User, related_name='secret_stories', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)

    objects = StoryManager()

    def __str__(self):
        return f'{self.id} {self.title}'


class PopularStory(models.Model):
    """
    인기 스토리
    rank 순위
    like_count 좋아요 개수 (base_past_second 기준 인기 스토리가 된 기준의 like_count)
    base_past_second 기준 과거 초 (인기 스토리가 된 기준의 과거 초) ex) 10 -> 현재로 부터 10초 전, 기준 생성한 like_count 용으로 사용
    is_deleted 삭제 여부
    """
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    rank = models.IntegerField(verbose_name='순위', db_index=True)
    like_count = models.IntegerField(verbose_name='좋아요 개수')
    base_past_second = models.IntegerField(verbose_name='기준 과거 초')
    is_deleted = models.BooleanField(verbose_name='삭제 여부', default=False, db_index=True)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)

    objects = PopularStoryManager()

    def __str__(self):
        return f'{self.id} {self.story.title}'


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
    solved_sheet_answer: 풀었던 정답
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
    solved_sheet_answer = models.ForeignKey(SheetAnswer, on_delete=models.SET_NULL, null=True)
    solving_status = models.CharField(
        max_length=20,
        choices=SOLVING_STATUS_CHOICES,
        default=SOLVING_STATUS_CHOICES[0][0],
        db_index=True,
    )
    start_time = models.DateTimeField(null=True)
    solved_time = models.DateTimeField(null=True)

    @classmethod
    def get_previous_user_sheet_answer_solves_with_current_sheet_id(cls, user_id: int, current_sheet_id: int):
        return list(
            cls.objects.select_related(
                'sheet',
                'next_sheet_path',
            ).filter(
                user_id=user_id,
                next_sheet_path__sheet_id=current_sheet_id,
                sheet__is_deleted=False,
                solving_status=cls.SOLVING_STATUS_CHOICES[1][0],
            ).values(
                'sheet_id',
                'sheet__title',
            )
        )

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

    def solved_sheet_action(self, solved_sheet_answer, next_sheet_path):
        from .services import get_story_email_subscription_emails
        self.answer = solved_sheet_answer.answer
        self.sheet_question = solved_sheet_answer.sheet.question
        self.solved_sheet_version = solved_sheet_answer.sheet.version
        self.solved_answer_version = solved_sheet_answer.version
        self.solved_sheet_answer = solved_sheet_answer
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
                'solved_sheet_answer',
                'next_sheet_path',
            ]
        )
        if StoryEmailSubscription.has_respondent_user(self.story_id, self.user_id):
            send_user_sheet_solved_email.apply_async(
                (
                    self.id,
                    get_story_email_subscription_emails(
                        int(self.story_id),
                        int(self.user_id),
                    )
                )
            )


class StoryEmailSubscription(models.Model):
    """
    story: 사용자가 풀고 있는 스토리
    respondent_user: Story 에서 행동에 대한 관찰할 user
    email: respondent_user 가 무언가를 했을 때, 이에 대한 이메일을 전송하기 위한 이메일 주소
    """
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True)
    respondent_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    email = models.CharField(verbose_name='이메일', max_length=100)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True)

    def __str__(self):
        return f'{self.id} {self.story_id} {self.respondent_user_id} {self.email}'

    class Meta:
        verbose_name = 'Story 관전을 위한 이메일'
        verbose_name_plural = 'Story 관전을 위한 이메일'

    @classmethod
    def has_respondent_user(cls, story_id, user_id):
        return cls.objects.filter(story_id=story_id, respondent_user=user_id).exists()


class StoryLike(models.Model):
    story = models.ForeignKey(Story, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(verbose_name='생성일', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='수정일', auto_now=True, db_index=True)

    class Meta:
        verbose_name = 'Story 좋아요'
        verbose_name_plural = 'Story 좋아요'

    def __str__(self):
        return f'{self.id} {self.story_id} {self.user_id}'

    @classmethod
    def get_active_story_like_count(cls, story_id):
        return cls.objects.filter(story_id=story_id, is_deleted=False).count()

    @classmethod
    def is_user_has_active_story_like(cls, user, story_id):
        if isinstance(user, AnonymousUser):
            return False
        return cls.objects.filter(user=user, story_id=story_id, is_deleted=False).exists()
