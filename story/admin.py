from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from hint.admin_forms import SheetHintInlineFormset, SheetHintAdminForm
from hint.models import SheetHint
from story.admin_forms import StoryAdminForm, SheetAdminForm
from story.models import Story, Sheet, SheetAnswer, NextSheetPath


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
        SheetHintInline,
    ]
    form = SheetAdminForm


class SheetAnswerAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'sheet_id',
        'answer',
        'answer_reply'
    ]


class NextSheetPathAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'story_id',
        'story_title',
        'next_sheet_path_sheet_id',
        'sheet_title',
        'next_sheet_path_sheet_answer_id',
        'answer_answer',
        'quantity',
    ]

    def story_id(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:story_story_change", args=[obj.sheet.story_id]),
            obj.sheet.story_id
        ))
    story_id.short_description = 'Story ID'

    def story_title(self, obj):
        return obj.sheet.story.title
    story_title.short_description = 'Story title'

    def next_sheet_path_sheet_id(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:story_sheet_change", args=[obj.sheet_id]),
            obj.sheet_id
        ))
    next_sheet_path_sheet_id.short_description = '정답을 맞춘 후, 다음 Sheet ID'

    def sheet_title(self, obj):
        return obj.sheet.title
    sheet_title.short_description = '정답을 맞춘 후, 다음 Sheet title'

    def next_sheet_path_sheet_answer_id(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:story_sheetanswer_change", args=[obj.answer_id]),
            obj.answer_id
        ))
    next_sheet_path_sheet_answer_id.short_description = '정답 ID'

    def answer_answer(self, obj):
        return obj.answer.answer
    answer_answer.short_description = '정답'

    def get_queryset(self, request):
        return super(NextSheetPathAdmin, self).get_queryset(
            request
        ).select_related(
            'sheet__story',
            'answer',
        )


admin.site.register(Story, StoryAdmin)
admin.site.register(Sheet, SheetAdmin)
admin.site.register(SheetAnswer, SheetAnswerAdmin)
admin.site.register(NextSheetPath, NextSheetPathAdmin)
