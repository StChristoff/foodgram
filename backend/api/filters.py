from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import User, Recipe, Tag


class IngredientFilter(SearchFilter):
    """
    Фильтр поиска по частичному вхождению в начале названия ингредиента.
    """
    search_param = 'name'


class RecipeFilter(FilterSet):
    """
    Фильтрация рецептов по:
    - избранному
    - автору
    - списку покупок.
    - тегам
    """
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart')
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorite__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(shopping_cart__author=self.request.user)
        return queryset
