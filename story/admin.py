from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from hint.admin_forms import SheetHintInlineFormset, SheetHintAdminForm, SheetAnswerAdminForm
from hint.models import SheetHint
from story.admin_forms import StoryAdminForm, SheetAdminForm
from story.models import Story, Sheet, SheetAnswer, NextSheetPath, StoryEmailSubscription, PopularStory, \
    UserSheetAnswerSolve, StorySlackSubscription, UserSheetAnswerSolveHistory, WrongAnswer


class StoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'description',
        'is_deleted',
        'created_at',
        'updated_at',
    ]
    form = StoryAdminForm


class SheetHintInline(admin.TabularInline):
    form = SheetHintAdminForm
    formset = SheetHintInlineFormset
    model = SheetHint
    extra = 0
    ordering = [
        'is_deleted',
        'sequence',
    ]


class SheetAnswerInline(admin.TabularInline):
    form = SheetAnswerAdminForm
    model = SheetAnswer
    extra = 0


class SheetAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'story_id',
        'title',
        'question',
        'is_deleted',
        'created_at',
        'updated_at',
    ]
    inlines = [
        SheetAnswerInline,
        SheetHintInline,
    ]
    form = SheetAdminForm


class SheetAnswerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'sheet_title',
        'answer',
        'answer_reply'
    ]

    def sheet_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_sheet_change", args=[obj.sheet_id]),
            obj.sheet.id,
            obj.sheet.title,
        ))
    sheet_title.short_description = 'Sheet title'

    def get_queryset(self, request):
        return super(SheetAnswerAdmin, self).get_queryset(
            request
        ).select_related(
            'sheet',
        )


class NextSheetPathAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'story_title',
        'answer_answer',
        'next_sheet_title',
        'quantity',
    ]

    def story_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_story_change", args=[obj.sheet.story_id]),
            obj.sheet.story_id,
            obj.sheet.story.title,
        ))
    story_title.short_description = 'Story title'

    def answer_answer(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_sheetanswer_change", args=[obj.answer_id]),
            obj.answer_id,
            obj.answer.answer,
        ))
    answer_answer.short_description = '정답'

    def next_sheet_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_sheet_change", args=[obj.sheet_id]),
            obj.sheet_id,
            obj.sheet.title,
        ))
    next_sheet_title.short_description = '정답을 맞춘 후, 다음 Sheet title'

    def get_queryset(self, request):
        return super(NextSheetPathAdmin, self).get_queryset(
            request
        ).select_related(
            'sheet__story',
            'answer',
        )


class StoryEmailSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'story',
        'respondent_user',
        'email',
    ]


class StorySlackSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'story',
        'respondent_user',
        'slack_webhook_url',
        'slack_channel_description',
    ]


class PopularStoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'story_title',
        'rank',
        'like_count',
        'base_past_second',
    ]

    def story_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_story_change", args=[obj.story_id]),
            obj.story_id,
            obj.story.title,
        ))
    story_title.short_description = 'Story title'

    def get_queryset(self, request):
        return super(PopularStoryAdmin, self).get_queryset(
            request
        ).select_related(
            'story',
        )


class UserSheetAnswerSolveAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_nickname',
        'story_title',
        'sheet_title',
        'next_sheet_path_sheet_title',
        'sheet_question',
        'user_answer',
        'solved_sheet_answer_answer',
        'solving_status',
        'start_time',
        'solved_time',
    ]

    def user_nickname(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:account_user_change", args=[obj.user_id]),
            obj.user.nickname,
        ))
    user_nickname.short_description = 'nickname'

    def story_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_story_change", args=[obj.story_id]),
            obj.story_id,
            obj.story.title,
        ))
    story_title.short_description = 'Story title'

    def sheet_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_sheet_change", args=[obj.sheet_id]),
            obj.sheet.id,
            obj.sheet.title,
        ))
    sheet_title.short_description = 'Sheet title'

    def next_sheet_path_sheet_title(self, obj):
        if obj.next_sheet_path and obj.next_sheet_path.sheet:
            return mark_safe('<a href="{}">[{}] {}</a>'.format(
                reverse("admin:story_sheet_change", args=[obj.next_sheet_path.sheet_id]),
                obj.next_sheet_path.sheet_id,
                obj.next_sheet_path.sheet.title,
            ))
    next_sheet_path_sheet_title.short_description = '다음 Sheet title'

    def user_answer(self, obj):
        return obj.answer
    user_answer.short_description = '유저가 작성한 정답'

    def solved_sheet_answer_answer(self, obj):
        if obj.solved_sheet_answer:
            return mark_safe('<a href="{}">[{}] {}</a>'.format(
                reverse("admin:story_sheetanswer_change", args=[obj.solved_sheet_answer.id]),
                obj.solved_sheet_answer_id,
                obj.solved_sheet_answer.answer,
            ))
    solved_sheet_answer_answer.short_description = '유저가 선택한 Sheet 정답'

    def get_queryset(self, request):
        return super(UserSheetAnswerSolveAdmin, self).get_queryset(
            request
        ).select_related(
            'user',
            'story',
            'sheet',
            'next_sheet_path__sheet',
            'solved_sheet_answer',
        )


class UserSheetAnswerSolveHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'group_id',
        'user_nickname',
        'story_title',
        'sheet_title',
        'next_sheet_path_sheet_title',
        'sheet_question',
        'user_answer',
        'solved_sheet_answer_answer',
        'solving_status',
        'start_time',
        'solved_time',
    ]

    def user_nickname(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:account_user_change", args=[obj.user_id]),
            obj.user.nickname,
        ))

    user_nickname.short_description = 'nickname'

    def story_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_story_change", args=[obj.story_id]),
            obj.story_id,
            obj.story.title,
        ))

    story_title.short_description = 'Story title'

    def sheet_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_sheet_change", args=[obj.sheet_id]),
            obj.sheet.id,
            obj.sheet.title,
        ))

    sheet_title.short_description = 'Sheet title'

    def next_sheet_path_sheet_title(self, obj):
        if obj.next_sheet_path and obj.next_sheet_path.sheet:
            return mark_safe('<a href="{}">[{}] {}</a>'.format(
                reverse("admin:story_sheet_change", args=[obj.next_sheet_path.sheet_id]),
                obj.next_sheet_path.sheet_id,
                obj.next_sheet_path.sheet.title,
            ))

    next_sheet_path_sheet_title.short_description = '다음 Sheet title'

    def user_answer(self, obj):
        return obj.answer

    user_answer.short_description = '유저가 작성한 정답'

    def solved_sheet_answer_answer(self, obj):
        if obj.solved_sheet_answer:
            return mark_safe('<a href="{}">[{}] {}</a>'.format(
                reverse("admin:story_sheetanswer_change", args=[obj.solved_sheet_answer.id]),
                obj.solved_sheet_answer_id,
                obj.solved_sheet_answer.answer,
            ))

    solved_sheet_answer_answer.short_description = '유저가 선택한 Sheet 정답'

    def get_queryset(self, request):
        return super(UserSheetAnswerSolveHistoryAdmin, self).get_queryset(
            request
        ).select_related(
            'user',
            'story',
            'sheet',
            'next_sheet_path__sheet',
            'solved_sheet_answer',
        )


class WrongAnswerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_nickname',
        'story_title',
        'sheet_title',
        'answer',
        'created_at',
    ]

    def user_nickname(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:account_user_change", args=[obj.user_id]),
            obj.user.nickname if obj.user else '',
        ))
    user_nickname.short_description = 'nickname'

    def story_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_story_change", args=[obj.story_id]),
            obj.story_id,
            obj.story.title,
        ))

    story_title.short_description = 'Story title'

    def sheet_title(self, obj):
        return mark_safe('<a href="{}">[{}] {}</a>'.format(
            reverse("admin:story_sheet_change", args=[obj.sheet_id]),
            obj.sheet.id,
            obj.sheet.title,
        ))

    sheet_title.short_description = 'Sheet title'


admin.site.register(Story, StoryAdmin)
admin.site.register(Sheet, SheetAdmin)
admin.site.register(SheetAnswer, SheetAnswerAdmin)
admin.site.register(NextSheetPath, NextSheetPathAdmin)
admin.site.register(StoryEmailSubscription, StoryEmailSubscriptionAdmin)
admin.site.register(StorySlackSubscription, StorySlackSubscriptionAdmin)
admin.site.register(PopularStory, PopularStoryAdmin)
admin.site.register(UserSheetAnswerSolve, UserSheetAnswerSolveAdmin)
admin.site.register(UserSheetAnswerSolveHistory, UserSheetAnswerSolveHistoryAdmin)
admin.site.register(WrongAnswer, WrongAnswerAdmin)
