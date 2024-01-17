import base64, re

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.http import Http404
from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Tag, Ingredient, Recipe, IngredientRecipe,
                            Favorite, ShoppingCart)
from users.models import User, Subscribe


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания модели User.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def validate_username(self, value):
        """
        Проверка корректности username.
        """
        if re.match(r'^[\w.@+-]+\Z', value):
            return value
        raise ValidationError('В Имени Пользователя могут быть только буквы, '
                              'цифры и знаки @/./+/-/_.')


class UserSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для модели User.
    Отображает:
    - Профиль текущего пользователя (me).
    - Профиль автора рецепта (по id).
    - Список пользователей.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscribe.objects.filter(user=user, author=obj).exists()
        return False


class ChangePasswordSerializer(SetPasswordSerializer):
    """
    Сериалайзер для смены пароля текущего пользователя.
    """
    new_password = serializers.CharField(write_only=True)
    current_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('new_password', 'current_password')

    def create(self, validated_data):
        user = User.objects.get(username=self.context.get('request').user)
        user.set_password(validated_data['new_password'])
        user.save()
        return Response('Пароль успешно изменен',
                        status=status.HTTP_204_NO_CONTENT)


class RecipeSubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для поля recipes в сериалайзере SubcriptionsSerializer.
    GET запросы.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения подписок текущего пользователя.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscribe.objects.filter(user=user, author=obj).exists()
        return False

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        limit = self.context.get('request').GET.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeSubscriptionsSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания/удаления подписки.
    """
    email = serializers.CharField(source='author.email', read_only=True)
    id = serializers.CharField(source='author.id', read_only=True)
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
            recipes = recipes[:int(limit)]
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
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для ингредиентов.
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


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для рецептов.
    Доступ:
    - Получение списка рецептов (LIST) и отдельного рецепта (DETAIL)- для всех.
    - Создание (POST) - только авторизованные пользователи.
    - Редактирование(PATCH) и удаление(DELETE) рецепта - только автор рецепта.

    """
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    author = UserSerializer(read_only=True,
                            default=serializers.CurrentUserDefault())
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
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'author'),
                message='Вы уже добавили рецепт с таким названием.'
            )
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        tags_data = TagSerializer(instance.tags, many=True).data
        data['tags'] = tags_data
        return data

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
                {'ingredients': 'Добавьте ингредиенты'})
        ingredients = validated_data.pop('ingredient_recipe')
        if 'tags' not in validated_data:
            raise serializers.ValidationError({'tags': 'Добавьте теги'})
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

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(author=user,
                                               recipe=obj).exists()
        return False

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError('Выберите тег.')
        unique_tags = []
        for tag in tags:
            if tag in unique_tags:
                raise ValidationError('Этот тег уже выбран.')
            unique_tags.append(tag)
        return value

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError('Выберите ингредиент.')
        unique_ingredients = []
        for ingredient in ingredients:
            if ingredient['ingredient']['id'] in unique_ingredients:
                raise ValidationError('Этот ингредиент уже добавлен.',
                                      code=status.HTTP_400_BAD_REQUEST)
            unique_ingredients.append(ingredient['ingredient']['id'])
            if ingredient['amount'] <= 0:
                raise ValidationError('Количество должно быть больше 0.',
                                      code=status.HTTP_400_BAD_REQUEST)
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления/удаления в избранное.
    """
    id = serializers.CharField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.CharField(source='recipe.image', read_only=True)
    cooking_time = serializers.CharField(source='recipe.cooking_time',
                                         read_only=True)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления/удаления в список покупок.
    """
    id = serializers.CharField(source='recipe.id', read_only=True)
    name = serializers.CharField(source='recipe.name', read_only=True)
    image = serializers.CharField(source='recipe.image', read_only=True)
    cooking_time = serializers.CharField(source='recipe.cooking_time',
                                         read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time')
