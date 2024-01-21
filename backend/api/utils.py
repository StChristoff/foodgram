from django.db.models import Sum
from django.http import HttpResponse

from recipes.models import IngredientRecipe


def download_cart(self, request, user):
    """
    Скачивание списка продуктов для выбранных рецептов пользователя.
    Файл в формате pdf.
    """
    ingredients_sum = IngredientRecipe.objects.filter(
        recipe__shopping_cart__author=user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amounts=Sum('amount')).order_by('ingredient__name')

    text = f'Список покупок ({user.first_name} {user.last_name})\n\n'
    for ingredient in ingredients_sum:
        text += (f'{ingredient["ingredient__name"]} - '
                 f'{ingredient["amounts"]} '
                 f'{ingredient["ingredient__measurement_unit"]}\n')

    file_name = f'Shopping_cart_{user.first_name}_{user.last_name}.txt'
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    response.write(text)
    return response
