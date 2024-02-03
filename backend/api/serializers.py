from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

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
            except ValueError:
                pass
        return RecipeSubscriptionsSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания/удаления подписки.
    Только POST и DELETE запросы.
    """

    class Meta:
        model = Subscribe
        fields = ('user', 'author')

    def to_representation(self, instance):
        serializer = SubscriptionsSerializer(instance.author,
                                             context=self.context)
        return serializer.data

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if Subscribe.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого автора',
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
    author = CustomUserSerializer(read_only=True)
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
    id = serializers.PrimaryKeyRelatedField(source='ingredient',
                                            queryset=Ingredient.objects.all())

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
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientRecipeCreateSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def to_representation(self, instance):
        serializer = RecipeGetSerializer(instance, context=self.context)
        return serializer.data

    def create_ingredient_recipe(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=ingredient['ingredient'],
                recipe=recipe,
                amount=ingredient['amount'])
             for ingredient in ingredients]
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=author)
        self.create_ingredient_recipe(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        self.create_ingredient_recipe(ingredients, instance)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise ValidationError({'ingredients': 'Выберите ингредиент.'},
                                  code=status.HTTP_400_BAD_REQUEST)
        unique_ingredients = set(
            [ingredient['ingredient'].id for ingredient in ingredients]
        )
        if len(unique_ingredients) != len(ingredients):
            raise ValidationError(
                {'ingredients': 'Повторяющиеся ингредиенты.'},
                code=status.HTTP_400_BAD_REQUEST
            )
        tags = data.get('tags')
        if not tags:
            raise ValidationError({'tags': 'Выберите тег.'},
                                  code=status.HTTP_400_BAD_REQUEST)
        unique_tags = set([tag.id for tag in tags])
        if len(unique_tags) != len(tags):
            raise ValidationError({'tags': 'Повторяющиеся теги.'},
                                  code=status.HTTP_400_BAD_REQUEST)
        image = data.get('image')
        if not image:
            raise serializers.ValidationError(
                {'image': 'Добавьте изображение.'},
                code=status.HTTP_400_BAD_REQUEST
            )
        return data


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
        serializer = FavoriteShopCartRecipeSerializer(instance.recipe)
        return serializer.data

    def validate(self, data):
        if Favorite.objects.filter(user=data.get('user'),
                                   recipe=data.get('recipe')).exists():
            raise ValidationError(
                {'errors': 'Вы уже добавили этот рецепт в избранное.'},
                code=status.HTTP_400_BAD_REQUEST)
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для добавления/удаления в список покупок.
    Только POST и DELETE запросы.
    """

    class Meta:
        model = ShoppingCart
        fields = ('author', 'recipe')

    def to_representation(self, instance):
        serializer = FavoriteShopCartRecipeSerializer(instance.recipe)
        return serializer.data

    def validate(self, data):
        if ShoppingCart.objects.filter(author=data.get('author'),
                                       recipe=data.get('recipe')).exists():
            raise ValidationError(
                {'errors': 'Вы уже добавили этот рецепт в список покупок.'},
                code=status.HTTP_400_BAD_REQUEST)
        return data
