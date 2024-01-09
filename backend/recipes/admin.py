from django.contrib import admin
from .models import Tag, Ingredient, Recipe, IngredientRecipe


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


class RecipeAdmin(admin.ModelAdmin):
    """
    Админ-зона рецептов.
    """
    list_display = ('id', 'name', 'text', 'cooking_time',
                    'author', 'pub_date',)
    filter_horizontal = ('tags',)
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'
    inlines = [IngredientRecipeInline]


class IngredientRecipeAdmin(admin.ModelAdmin):
    """
    Админ-зона модели связи Ингредиент-Рецепт.
    """
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    empty_value_display = '-пусто-'


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
