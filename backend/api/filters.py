from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

# from recipes.models import User, Recipe, Tag


class IngredientFilter(SearchFilter):
    """
    Фильтр поиска по частичному вхождению в начале названия ингредиента.
    """
    search_param = 'name'


class RecipeFilter(FilterSet):
    pass