from rest_framework import permissions


class CMSUserPermission(permissions.BasePermission):
    message = 'No Auth'

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.user_type_id == 1
