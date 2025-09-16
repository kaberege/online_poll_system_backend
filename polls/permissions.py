from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    - Anyone can read polls (SAFE_METHODS).
    - Only authenticated users can create.
    - Only the owner can update/delete their poll.
    - Polls cannot be updated if expired.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in ["PUT", "PATCH"] and obj.is_expired:
            return False
        return obj.owner == request.user
