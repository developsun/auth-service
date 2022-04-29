from rest_framework import permissions


class AnonymousUserOnlyPermission(permissions.BasePermission):
    """
    Custom permission to ensure user is not authorized and is anonymous
    """
    message = "Mustn't be authorized to perform this action"

    def has_permission(self, request, *args, **kwargs):
        if request.user.pk is None:
            return True
        return False
