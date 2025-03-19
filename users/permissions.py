from rest_framework.permissions import BasePermission


class IsUpdatingOwnAccount(BasePermission):

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return obj == request.user
