from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        print(repr(obj.owner) + "request:" + repr(request.user))
        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


class AppVersionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        version_code = request.META.get('versionCode')
        if version_code is None or version_code < 101:
            return False
        return True
