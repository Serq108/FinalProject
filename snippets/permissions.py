from rest_framework import permissions


def entry_check(strn, list_str):
    entering = False
    for item in list_str:
        if strn == item:
            entering = True
    return entering


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        if obj.owner == request.user:
            return True
        return bool(request.user and request.user.is_staff)


class IsUserOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the owner of the snippet.
        if obj.id == request.user.id:
            return True
        return bool(request.user and request.user.is_staff)

class IfGroup2(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.perm_list:
            prmsn_list = [id for id in obj.perm_list.split(',') if id]
            # ~ print('LIST', prmsn_list)
            # ~ print('ID', request.user.id)
            if entry_check(str(request.user.id), prmsn_list):
                return True
        if request.user.groups.filter(name='Tutors').exists():
            return True
        return bool(request.user and request.user.is_staff)


class IfOwnerSnippet(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.owner_id == request.user.id:
            return True
        return bool(request.user and request.user.is_staff)
