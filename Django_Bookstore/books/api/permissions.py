
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Владелец может изменять объект.
    Остальные могут только читать, если имеют доступ.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user.is_authenticated
            and obj.user_id == request.user.id
        )
