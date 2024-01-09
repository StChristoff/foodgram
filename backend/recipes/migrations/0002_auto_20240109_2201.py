# Generated by Django 3.2.6 on 2024-01-09 19:01

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IngredientRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(help_text='Укажите количество выбранного ингредиента', verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Связь рецепта и ингредиента',
                'verbose_name_plural': 'Связи рецептов и ингредиентов',
            },
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(default=0, help_text='Выберите Автора рецепта', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to='users.user', verbose_name='Автор рецепта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(default=1, help_text='Введите время приготовления блюда в минутах', validators=[django.core.validators.MinValueValidator(1, 'Минимальное время приготовления - 1 минута')], verbose_name='Время приготовления'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=1, help_text='Добавьте изображение готового блюда', upload_to='recipes_img/', verbose_name='Изображение блюда'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='name',
            field=models.CharField(db_index=True, default=1, help_text='Введите название рецепта', max_length=200, verbose_name='Название рецепта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата публикации'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите Тег', to='recipes.Tag', verbose_name='Название тега'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='text',
            field=models.TextField(default=1, help_text='Опишите способ приготовления блюда', verbose_name='Описание рецепта'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('name', 'author'), name='Уникальный рецепт'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(help_text='Выберите ингредиент', on_delete=django.db.models.deletion.CASCADE, to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AddField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(help_text='Выберите рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_recipe', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(help_text='Выберите ингредиент', through='recipes.IngredientRecipe', to='recipes.Ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='Уникальный ингредиент в рецепте'),
        ),
    ]
