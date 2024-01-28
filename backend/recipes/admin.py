from django.contrib import admin
from .models import (Tag, Ingredient, Recipe, IngredientRecipe,
                     Favorite, ShoppingCart)


class TagAdmin(admin.ModelAdmin):
    """
    Админ-зона тегов.
    """
    list_display = ('id', 'name', 'color', 'slug',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    """
    Админ-зона ингредиентов.
    """
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientRecipeInline(admin.TabularInline):
    """
    Создание поля добавления ингредиентов и их количества
    при создании рецепта в админ-зоне.
    """
    model = IngredientRecipe
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-зона рецептов.
    """
    list_display = ('id', 'name', 'text', 'cooking_time',
                    'author', 'pub_date', 'in_favorite')
    filter_horizontal = ('tags',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'
    inlines = [IngredientRecipeInline]

    def in_favorite(self, obj):
        return obj.favorite.all().count()

    in_favorite.short_description = 'В избранном у других пользователей'


class IngredientRecipeAdmin(admin.ModelAdmin):
    """
    Админ-зона модели связи Ингредиент-Рецепт.
    """
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    """
    Админ-зона избранных рецептов.
    """
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user',)


class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Админ-зона списка покупок.
    """
    list_display = ('author', 'recipe')
    list_filter = ('author',)
    search_fields = ('author',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
