from django.contrib import admin
from .models import Tag, Ingredient, Recipe


class TagAdmin(admin.ModelAdmin):
    """
    Админ-зона тегов.
    """
    list_display = ('id', 'name', 'color', 'slug',)
    list_filter = ('id',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-зона ингредиентов.
    """
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
