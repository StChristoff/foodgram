from django.db import models
from django.core.validators import MinValueValidator

from foodgram.settings import COLOR_LEN, NAME_LEN, SLUG_LEN, SYM_NUM

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
    Модель тега для рецепта.
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
    """
    Модель ингредиента для рецепта.
    """
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
    """
    Модель рецепта блюда.
    """
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=NAME_LEN,
        help_text='Введите название рецепта',
        db_index=True,
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        upload_to='recipes_img/',
        help_text='Добавьте изображение готового блюда',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Опишите способ приготовления блюда',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления блюда в минутах',
        validators=[MinValueValidator(
            1, 'Минимальное время приготовления - 1 минута')],
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Выберите Автора рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientRecipe',
        help_text='Выберите ингредиент',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        help_text='Выберите Тег',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='Уникальный рецепт',
            )
        ]

    def __str__(self):
        return self.name[:SYM_NUM]


class IngredientRecipe(models.Model):
    """
    Модель для связи Ingredient и Recipe
    """
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        help_text='Выберите ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        help_text='Выберите рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество выбранного ингредиента',
    )

    class Meta:
        verbose_name = 'Связь рецепта и ингредиента'
        verbose_name_plural = 'Связи рецептов и ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='Уникальный ингредиент в рецепте',
            )
        ]

    def __str__(self):
        return (f'{self.ingredient}-{self.amount} '
                f'{self.ingredient.measurement_unit}, '
                f'в рецепте "{self.recipe}"')


class Favorite(models.Model):
    """
    Модель для избранных рецептов.
    Связь избранных рецептов и пользователя.
    """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite',
        help_text='Выберите Пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранный рецепт',
        on_delete=models.CASCADE,
        related_name='favorite',
        help_text='Выберите рецепт',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Уникальная пара для модели избранных рецептов',
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    """
    Модель для списка покупок пользователя.
    Связь пользователя и рецепта в списке покупок.
    """
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        help_text='Выберите Пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт для списка покупок',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        help_text='Выберите рецепт для списка покупок',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'recipe'],
                name='Уникальная пара для модели списка покупок.',
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в списке покупок у {self.author}'
