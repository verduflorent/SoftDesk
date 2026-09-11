from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Allow contributors to read a resource, but only its author to change it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsProjectAuthorOrReadOnly(permissions.BasePermission):
    """Allow project contributors to read memberships, but only the project author to change them."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.project.author == request.user
