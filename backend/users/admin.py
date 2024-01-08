from django.contrib import admin
from .models import User, Subscribe


class UserAdmin(admin.ModelAdmin):
    """
    Админ-зона пользователей.
    """
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


class SubscribeAdmin(admin.ModelAdmin):
    """
    Админ-зона подписок.
    """
    list_display = ('id', 'user', 'author')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscribeAdmin)
