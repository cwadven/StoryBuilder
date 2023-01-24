from django.contrib import admin

from hint.models import SheetHint, UserSheetHintHistory


admin.site.register(SheetHint)
admin.site.register(UserSheetHintHistory)
