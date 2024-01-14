import io, os, subprocess, webbrowser
# import os
# import subprocess
# import webbrowser
from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from reportlab.lib import fonts
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from recipes.models import IngredientRecipe
from foodgram.settings import BASE_DIR

START_X = 50
START_Y = 800
HEAD_OFFSET = 170

# def download_cart(self, request, user):
#     """
#     Скачивание списка продуктов для выбранных рецептов пользователя.
#     Файл в формате txt.
#     """
#     buffer = io.BytesIO()
#     text = canvas.Canvas(buffer)
#     ingredients_sum = IngredientRecipe.objects.filter(
#         recipe__shopping_cart__author=user
#     ).values(
#         'ingredient__name', 'ingredient__measurement_unit'
#     ).annotate(amounts=Sum('amount')).order_by('ingredient__name')
#     text.drawString(
#         START_X,
#         START_Y,
#         f'Список покупок ({user.first_name} {user.last_name})')
#     start_y = START_Y - 30
#     # shopping_cart = (f'Список покупок ({user.first_name} {user.last_name})\n')
#     for ingredient in ingredients_sum:
#         text.drawString(
#             START_X,
#             start_y,
#             (f'{ingredient.ingredient.name} - '
#              f'{ingredient.amount}'
#              f'{ingredient.ingredient.measurement_unit}')
#         )
#         start_y -= 15
#     text.showPage()
#     text.save()
#     buffer.seek(0)
#     return FileResponse(
#         buffer,
#         as_attachment=True,
#         filename=f'Shopping_cart_{user.first_name}_{user.last_name}.pdf'
#     )


def download_cart(self, request, user):
    """
    Скачивание списка продуктов для выбранных рецептов пользователя.
    Файл в формате pdf.
    """
    pdf_filename = f'Shopping_cart_{user.first_name}_{user.last_name}.pdf'

    new_folder_path = f'{BASE_DIR}\\shopping_carts\\'
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
    pdf_file_path = os.path.join(new_folder_path, pdf_filename)

    text = canvas.Canvas(pdf_file_path)

    font_file_path = f'{BASE_DIR}\\fonts\\Arial.ttf'
    pdfmetrics.registerFont(TTFont('Arial', font_file_path))
    text.setFont('Arial', 12)

    ingredients_sum = IngredientRecipe.objects.filter(
        recipe__shopping_cart__author=user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(amounts=Sum('amount')).order_by('ingredient__name')
    text.drawString(
        START_X + HEAD_OFFSET,
        START_Y,
        f'Список покупок ({user.first_name} {user.last_name})')
    start_y = START_Y - 30
    for ingredient in ingredients_sum:
        text.drawString(
            START_X,
            start_y,
            (f'{ingredient["ingredient__name"]} - '
             f'{ingredient["amounts"]} '
             f'{ingredient["ingredient__measurement_unit"]}')
        )
        start_y -= 15
    text.showPage()
    text.save()
    subprocess.Popen([pdf_file_path], shell=True)
    response = HttpResponse(text, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={pdf_filename}'
    return response

    # subprocess.Popen([pdf_filename], shell=True)
    # webbrowser.open(f'Shopping_cart_{user.first_name}_{user.last_name}.pdf')
    # return HttpResponse(text, content_type='text/plain')


# def download_cart(self, request, user):
#     """
#     Скачивание списка продуктов для выбранных рецептов пользователя
#     в txt формате
#     """
#     sum_ingredients_in_recipes = IngredientRecipe.objects.filter(
#         recipe__shopping_cart__author=user
#     ).values(
#         'ingredient__name', 'ingredient__measurement_unit'
#     ).annotate(
#         amounts=Sum('amount', distinct=True)).order_by('amounts')
#     shopping_list = f'Список покупок ({user.first_name} {user.last_name})\n'
#     for ingredient in sum_ingredients_in_recipes:
#         shopping_list += (
#             f'{ingredient["ingredient__name"]} - '
#             f'{ingredient["amounts"]} '
#             f'{ingredient["ingredient__measurement_unit"]}\n'
#         )
#     shopping_list += '\n\nFoodgram (2022)'
#     filename = 'shopping_list.txt'
#     response = HttpResponse(shopping_list, content_type='text/plain')
#     response['Content-Disposition'] = f'attachment; filename={filename}'
#     return response
