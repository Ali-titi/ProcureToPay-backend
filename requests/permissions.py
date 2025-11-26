from rest_framework import permissions


class IsStaff(permissions.BasePermission):
    """Only staff can create and manage their own requests"""

    def has_permission(self, request, view):
        return request.user.role == 'staff'

    def has_object_permission(self, request, view, obj):
        # Staff can only access their own requests
        return obj.created_by == request.user


class IsApprover(permissions.BasePermission):
    """Approvers can view and act on requests in their level"""

    def has_permission(self, request, view):
        return request.user.role in ['approver1', 'approver2']

    def has_object_permission(self, request, view, obj):
        # Approvers can view requests they can approve
        return obj.can_approve(request.user)


class IsFinance(permissions.BasePermission):
    """Finance can view approved requests and manage documents"""

    def has_permission(self, request, view):
        return request.user.role == 'finance'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Staff can edit their own pending requests, others can read"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user and obj.can_edit()


class IsAdmin(permissions.BasePermission):
    """Admin has full access"""

    def has_permission(self, request, view):
        return request.user.role == 'admin'


class CanApproveRequest(permissions.BasePermission):
    """Check if user can approve/reject the specific request"""

    def has_object_permission(self, request, view, obj):
        return obj.can_approve(request.user)