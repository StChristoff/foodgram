from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .serializers import (UserCreateSerializer, UserSerializer,
                          ChangePasswordSerializer, SubscriptionsSerializer,
                          SubscribeSerializer, TagSerializer,
                          IngredientSerializer, RecipeSerializer,
                          RecipeCreateSerializer)
from recipes.models import Tag, Ingredient, Recipe, IngredientRecipe
from users.models import User, Subscribe


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для:
    - UserCreateSerializer: Создание пользователя
    - UserSerializer:
      Просмотр списка пользователей.
    Доступ:
    - Просмотр списка пользователей - для всех.
    - Создание пользователя - для всех.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny, )
    # pagination_class = ApiPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer


class UserMeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для просмотра собственного профиля.
    Доступ:
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )

    def get_queryset(self):
        return User.objects.filter(username=self.request.user)


class PasswordChangeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для смены пароля.
    Доступ:
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (AllowAny, )


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для для просмотра подписок текущего пользователя.
    Доступ:
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = SubscriptionsSerializer
    permission_classes = (AllowAny, )

    def get_queryset(self):
        return User.objects.filter(followed__user=self.request.user)


# class SubscribeViewSet(mixins.DestroyModelMixin, mixins.CreateModelMixin,
#                        viewsets.GenericViewSet):
class SubscribeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для создания/отмены подписки.
    Доступ:
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = SubscribeSerializer
    permission_classes = (AllowAny, )
    http_method_names = ['delete', 'post',]

    def perform_create(self, serializer):
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if Subscribe.objects.filter(user=user, author=author).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST)
        if author == user:
            return Response(
                {'errors': 'Вы не можете подписаться на себя'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer.save(author=author, user=user)
        return Response(
            {'Подписка успешно создана': serializer.data},
            status=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        author = User.objects.get(id=self.kwargs.get('id'))
        user = self.request.user
        instance = get_object_or_404(Subscribe, user=user, author=author)
        if instance:
            instance.delete()
            return Response(
                'Успешная отписка', status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для:
    - Получения списка тегов.
    - Получения отдельного тега.
    Доступ:
    - Чтение - для всех.
    - Запись - недоступна.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    http_method_names = ['get',]


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для:
    - Получения списка ингредиентов.
    - Получения отдельного ингредиента.
    Доступ:
    - Чтение - для всех.
    - Запись - недоступна.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (IngredientFilter, )
    search_fields = ('^name',)
    http_method_names = ['get',]


lass RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для.
    - Получения списка рецептов.
    - Создания рецепта.
    - Получения отдельного рецепта.
    - Редактирования рецепта.
    - Удаления рецепта.
    Доступ:
    - Чтение - для всех.
    - Запись:
      - Создание рецепта - аутентифицированный пользователь.
      - Редактирование рецепта - только автор или администратор.
      - Удаление рецепта - только автор или администратор.
    """
    queryset = Recipe.objects.select_related('author')
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    # pagination_class = ApiPagination
    # filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer