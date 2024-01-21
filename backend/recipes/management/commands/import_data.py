import json

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда импорта данных из файла *json в базу данных sqlite"""

    help = "Импорт данных"

    def handle(self, *args, **kwargs):
        json_file_path = f'{BASE_DIR}/data/ingredients.json'
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for item in data:
                obj = Ingredient(
                    name=item['name'],
                    measurement_unit=item['measurement_unit'],
                )
                obj.save()
        print('База данных заполнена')
