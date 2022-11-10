from django.contrib import admin

from account.models import (
    User,
    UserProvider,
    UserStatus,
    UserType
)


class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nickname',
        'user_type',
        'user_status',
        'user_provider',
    ]


class UserProviderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'description'
    ]


class UserUserStatusAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'description'
    ]


class UserUserTypeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
        'description'
    ]


admin.site.register(User, UserAdmin)
admin.site.register(UserProvider, UserProviderAdmin)
admin.site.register(UserStatus, UserUserStatusAdmin)
admin.site.register(UserType, UserUserTypeAdmin)
