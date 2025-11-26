from rest_framework import permissions


class IsAuthenticatedUser(permissions.BasePermission):
    """Allow authenticated users to access their own data"""

    def has_object_permission(self, request, view, obj):
        return obj == request.user