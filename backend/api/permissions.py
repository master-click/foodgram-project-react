from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request):
        return (
            request.method in ('GET',) or request.user.is_authenticated
            and request.user.is_admin
        )