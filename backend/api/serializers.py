import base64
from django.core.files.base import ContentFile
from djoser.serializers import SetPasswordSerializer
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Tag, Ingredient, Recipe, IngredientRecipe
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
        return Response(
            'Пароль успешно изменен',
            status=status.HTTP_204_NO_CONTENT
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения подписок текущего пользователя.
    """
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    # recipes = RecipeSerializer(read_only=True, many=True)
    # recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscribe.objects.filter(user=user, author=obj).exists()
        return False


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания подписки.
    """
    email = serializers.CharField(source='author.email', read_only=True)
    id = serializers.CharField(source='author.id', read_only=True)
    username = serializers.CharField(source='author.username', read_only=True)
    first_name = serializers.CharField(source='author.first_name',
                                       read_only=True)
    last_name = serializers.CharField(source='author.last_name',
                                      read_only=True)
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Subscribe.objects.filter(user=user,
                                            author=obj.author).exists()
        return False


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
    Сериалайзер для получения списка рецептов и отдельного рецепта.
    GET запросы.
    """
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='ingredient_recipe')
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  # 'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    # def get_is_favorited(self, obj):
    #     user = self.context.get('request').user
    #     if not user.is_anonymous:
    #         return Favorite.objects.filter(user=user, recipe=obj).exists()
    #     return False

    # def get_is_in_shopping_cart(self, obj):
    #     user = self.context.get('request').user
    #     if not user.is_anonymous:
    #         return ShoppingCart.objects.filter(author=user, recipe=obj).exists()
    #     return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания, редактирования и удаления рецепта.
    POST, PATCH и DELETE запросы.
    """
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    # tags = TagSerializer(many=True) # queryset=Tag.objects.all())
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='ingredient_recipe')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        print(f'-----------validated_data={validated_data}')
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        print(f'-----------ingredients={ingredients}')
        print(f'-----------tags={tags}')
        recipe = Recipe.objects.create(**validated_data)
        print(f'-----------recipe={recipe}')
        for ingredient in ingredients:
            print(f'-----------ingredient={ingredient["amount"]}')
            current_ingredient, status = Ingredient.objects.get_or_create(
                name=ingredient['ingredient']['id'],
                measurement_unit=ingredient["ingredient"]["id"].measurement_unit)
            IngredientRecipe.objects.create(
                ingredient=current_ingredient,
                recipe=recipe,
                amount=ingredient["amount"])
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        print(f'-----------validated_data={validated_data}')
        print(f'-----------instance={instance}')
        ingredients = validated_data.pop('ingredient_recipe')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        for ingredient in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])
        instance.tags.set(tags)
        return super().update(instance, validated_data)