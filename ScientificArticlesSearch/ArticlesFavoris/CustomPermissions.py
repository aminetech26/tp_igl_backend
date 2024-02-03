from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type=='Admin')

class IsModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.user_type=='Moderator')
    
class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.auth)
