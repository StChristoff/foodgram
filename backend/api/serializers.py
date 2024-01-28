import base64
import re

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Tag, Ingredient, Recipe, IngredientRecipe,
                            Favorite, ShoppingCart)
from users.models import User, Subscribe


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для модели User.
    Отображает:
    - Профиль текущего пользователя (me).
    - Профиль автора рецепта (по id).
    - Список пользователей.
    GET и POST запросы.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return bool(
            self.context.get('request')
            and self.context.get('request').user.is_authenticated
            and Subscribe.objects.filter(
                user=self.context.get('request').user,
                author=obj
            ).exists()
        )


class RecipeSubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для поля recipes в сериалайзерах SubcriptionsSerializer,
    и SubscribeSerializer
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(CustomUserSerializer):
    """
    Сериалайзер для отображения подписок текущего пользователя.
    Только GET запросы.
    """
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        limit = self.context.get('request').GET.get('recipes_limit')
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValidationError:
                raise ValidationError({'errors': 'Неверный формат limit'},
                                      code=status.HTTP_400_BAD_REQUEST)
        return RecipeSubscriptionsSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания/удаления подписки.
    Только POST и DELETE запросы.
    """
    email = serializers.CharField(source='author.email', read_only=True)
    id = serializers.IntegerField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name',
                                       read_only=True)
    last_name = serializers.CharField(source='author.last_name',
                                      read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return Subscribe.objects.filter(user=user, author=obj.author).exists()

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        limit = self.context.get('request').GET.get('recipes_limit')
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValidationError:
                raise ValidationError({'errors': 'Неверный формат limit'},
                                      code=status.HTTP_400_BAD_REQUEST)
        return RecipeSubscriptionsSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        pk = self.context['request'].parser_context['kwargs']['pk']
        user = self.context.get('request').user
        author = get_object_or_404(User, id=pk)
        if Subscribe.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого автора.',
                                  code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError('Нельзя подписаться на себя.',
                                  code=status.HTTP_400_BAD_REQUEST)
        return data


class TagSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для тегов.
    Только GET запросы.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для ингредиентов.
    Только GET запросы.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('name', 'measurement_unit',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для получения ингредиентов в сериалайзере RecipeSerializer.
    """
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для получения рецептов.
    Доступ для всех.
    """
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='ingredient_recipe')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        return bool(
            self.context.get('request')
            and self.context.get('request').user.is_authenticated
            and Favorite.objects.filter(
                user=self.context.get('request').user,
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return bool(
            self.context.get('request')
            and self.context.get('request').user.is_authenticated
            and ShoppingCart.objects.filter(
                author=self.context.get('request').user,
                recipe=obj
            ).exists()
        )


class IngredientRecipeCreateSerializer(IngredientRecipeSerializer):
    """
    Сериалайзер для отображения ингредиентов в 
    сериалайзере RecipeCreateSerializer.
    """
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(RecipeGetSerializer):
    """
    Сериалайзер для создания, редактирования и удаления рецептов.
    Доступ:
    - Создание (POST) - только авторизованные пользователи.
    - Редактирование (PATCH) и удаление (DELETE) - только автор рецепта.

    """
    author = CustomUserSerializer(read_only=True,
                                  default=serializers.CurrentUserDefault())
    ingredients = IngredientRecipeCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def to_representation(self, instance):
        return super().to_representation(instance)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                name=ingredient['ingredient']['id'],
                measurement_unit=ingredient['ingredient']['id'].
                measurement_unit
            )
            IngredientRecipe.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient['amount'])
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredient_recipe' not in validated_data:
            raise serializers.ValidationError(
                {'ingredients': 'Добавьте ингредиенты'},
                code=status.HTTP_400_BAD_REQUEST)
        ingredients = validated_data.pop('ingredient_recipe')
        if 'tags' not in validated_data:
            raise serializers.ValidationError({'tags': 'Добавьте теги'},
                                              code=status.HTTP_400_BAD_REQUEST)
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        for ingredient in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount'])
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({'tags': 'Выберите тег.'},
                                  code=status.HTTP_400_BAD_REQUEST)
        unique_tags = []
        for tag in tags:
            if tag in unique_tags:
                raise ValidationError({'tags': 'Этот тег уже выбран.'},
                                      code=status.HTTP_400_BAD_REQUEST)
            unique_tags.append(tag)
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({'ingredients': 'Выберите ингредиент.'},
                                  code=status.HTTP_400_BAD_REQUEST)
        unique_ingredients = []
        for ingredient in ingredients:
            if ingredient['ingredient']['id'] in unique_ingredients:
                raise ValidationError(
                    {'ingredients': 'Этот ингредиент уже добавлен.'},
                    code=status.HTTP_400_BAD_REQUEST)
            unique_ingredients.append(ingredient['ingredient']['id'])
            if ingredient['amount'] <= 0:
                raise ValidationError(
                    {'errors': 'Количество ингредиента должно быть больше 0.'},
                    code=status.HTTP_400_BAD_REQUEST)
        return value


class FavoriteShopCartRecipeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения рецептов в сериалайзерах 
    FavoriteSerializer и ShoppingCartSerializer.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления/удаления в избранное.
    Только POST и DELETE запросы.
    """

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def to_representation(self, instance):
        print(f'\n------Сработал def to_representation')
        print(f'------instance={instance}')
        print(f'------instance.recipe={instance.recipe}\n')

        data = super().to_representation(instance)
        recipe_data = FavoriteShopCartRecipeSerializer(instance.recipe).data
        data['recipe'] = recipe_data
        return data

    def validate(self, data):
        print(f'\n------Сработал def validate')
        print(f'------data={data}\n')

        pk = self.context['request'].parser_context['kwargs']['pk']
        user = self.context.get('request').user
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            raise ValidationError({'errors': 'Рецепт не найден'},
                                  code=status.HTTP_400_BAD_REQUEST)
        if Favorite.objects.filter(user=user,
                                   recipe=recipe).exists():
            raise ValidationError(
                {'errors': 'Вы уже добавили этот рецепт в избранное.'},
                code=status.HTTP_400_BAD_REQUEST)
        return data


# class FavoriteSerializer(serializers.ModelSerializer):
#     """
#     Сериалайзер для добавления/удаления в избранное.
#     Только POST и DELETE запросы.
#     """
#     id = serializers.IntegerField(source='recipe.id', read_only=True)
#     name = serializers.CharField(source='recipe.name', read_only=True)
#     image = serializers.CharField(source='recipe.image', read_only=True)
#     cooking_time = serializers.IntegerField(source='recipe.cooking_time',
#                                             read_only=True)

#     class Meta:
#         model = Favorite
#         fields = ('id', 'name', 'image', 'cooking_time')

#     def validate(self, data):
#         pk = self.context['request'].parser_context['kwargs']['pk']
#         user = self.context.get('request').user
#         try:
#             recipe = Recipe.objects.get(id=pk)
#         except Recipe.DoesNotExist:
#             raise ValidationError({'errors': 'Рецепт не найден'},
#                                   code=status.HTTP_400_BAD_REQUEST)
#         if Favorite.objects.filter(user=user,
#                                    recipe=recipe).exists():
#             raise ValidationError(
#                 {'errors': 'Вы уже добавили этот рецепт в избранное.'},
#                 code=status.HTTP_400_BAD_REQUEST)
#         return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления/удаления в список покупок.
    Только POST и DELETE запросы.
    """
    id = serializers.IntegerField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.CharField(source='recipe.image', read_only=True)
    cooking_time = serializers.IntegerField(source='recipe.cooking_time',
                                            read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        pk = self.context['request'].parser_context['kwargs']['pk']
        user = self.context.get('request').user
        try:
            recipe = Recipe.objects.get(id=pk)
        except Recipe.DoesNotExist:
            raise ValidationError({'errors': 'Рецепт не найден'},
                                  code=status.HTTP_400_BAD_REQUEST)
        if ShoppingCart.objects.filter(author=user,
                                       recipe=recipe).exists():
            raise ValidationError(
                {'errors': 'Вы уже добавили этот рецепт в список покупок.'},
                code=status.HTTP_400_BAD_REQUEST)
        return data
