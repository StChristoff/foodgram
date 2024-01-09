from django.contrib import admin
from .models import Tag, Ingredient, Recipe, IngredientRecipe


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


class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-зона рецептов.
    """
    list_display = ('id', 'name', 'text', 'cooking_time', 'author', 'ingredients', 'tags', 'pub_date')
    list_filter = ('-pub_date',)
    empty_value_display = '-пусто-'


class IngredientRecipeAdmin(admin.ModelAdmin):
    """
    Админ-зона модели связи Ингредиент-Рецепт.
    """
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    list_filter = ('id',)
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
