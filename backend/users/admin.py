from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    """
    Админ-зона пользователей.
    """
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
