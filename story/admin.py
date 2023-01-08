from django.contrib import admin

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
        'sheet_id',
        'sheet_title',
        'answer_id',
        'answer_answer',
        'quantity',
    ]

    def answer_answer(self, obj):
        return obj.answer.answer
    answer_answer.short_description = '정답'

    def sheet_title(self, obj):
        return obj.sheet.title
    sheet_title.short_description = '정답을 맞춘 후, 다음 시트 title'

    def story_id(self, obj):
        return obj.sheet.story_id
    story_id.short_description = 'Story ID'

    def story_title(self, obj):
        return obj.sheet.story.title
    story_title.short_description = 'Story title'

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
