from rest_framework import permissions


class IsWebMasterAdminOrReadonly(permissions.BasePermission):

    def has_permission(self, request, view):
        g = request.user.groups.filter(name = "webMaster").exists()
        if request.method in permissions.SAFE_METHODS:
            return True
        return g or request.user.is_staff


class IsWebMasterOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        g = request.user.groups.filter(name = "webMaster").exists()
        return g or request.user.is_staff