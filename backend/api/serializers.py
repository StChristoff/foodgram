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
    name = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        # read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для получения ингредиентов в сериалайзере RecipeSerializer.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для списка рецептов и отдельного рецепта.
    GET, POST и PATCH запросы.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredient_recipe',
        read_only=True)
    # is_favorited = serializers.SerializerMethodField()
    # is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  # 'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

