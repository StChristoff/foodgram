from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Неавторизованные пользователи - только чтение.
    Авторизованные пользователи - чтение и создание объекта.
    Автору разрешены методы записи (PATCH, DELETE) над своими объектами.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
