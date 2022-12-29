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
        'sheet_id',
        'answer_id',
        'quantity',
    ]


admin.site.register(Story, StoryAdmin)
admin.site.register(Sheet, SheetAdmin)
admin.site.register(SheetAnswer, SheetAnswerAdmin)
admin.site.register(NextSheetPath, NextSheetPathAdmin)
