from rest_framework import permissions


class IsFinanceUser(permissions.BasePermission):
    """Only finance users can access finance endpoints"""

    def has_permission(self, request, view):
        return request.user.role == 'finance'