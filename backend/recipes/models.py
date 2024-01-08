from django.db import models
from django.db.models import Q, F
from django.core.validators import MinValueValidator

from foodgram.settings import (COLOR_LEN, NAME_LEN, SLUG_LEN, SYM_NUM)

from users.models import User

ORANGE = 'ff8000'
GREEN = '008000'
BLUE = '0096ff'
COLOR_CHOICES = (
    (ORANGE, 'Оранжевый'),
    (GREEN, 'Зеленый'),
    (BLUE, 'Синий'),
)


class Tag(models.Model):
    """
    Теги для рецепта.
    """
    name = models.CharField(
        verbose_name='Имя тега',
        max_length=NAME_LEN,
        unique=True,
        help_text='Введите имя тега',
    )
    color = models.CharField(
        verbose_name='Цвет тега',
        max_length=COLOR_LEN,
        unique=True,
        choices=COLOR_CHOICES,
        help_text='Выберите цвет',
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=SLUG_LEN,
        unique=True,
        help_text='Укажите слаг',
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель ингредиента блюда."""
    name = models.CharField(
        verbose_name='Наименование ингредиента',
        max_length=NAME_LEN,
        help_text='Введите наименование ингредиента',
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=SLUG_LEN,
        help_text='Введите единицу измерения',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:SYM_NUM]


class Recipe(models.Model):
    pass