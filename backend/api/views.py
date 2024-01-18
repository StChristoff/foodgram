from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnly, IsAuthenticatedOrReadCreateOnly
from .serializers import (UserCreateSerializer, UserSerializer,
                          ChangePasswordSerializer, SubscriptionsSerializer,
                          SubscribeSerializer, TagSerializer,
                          IngredientSerializer, RecipeSerializer,
                          FavoriteSerializer, ShoppingCartSerializer)
from .utils import download_cart
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from users.models import User, Subscribe


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для:
    - UserCreateSerializer: Создание пользователя
    - UserSerializer:
      Просмотр списка пользователей.
    Доступ:
    - Просмотр списка пользователей (UserSerializer) - для всех.
    - Создание пользователя (UserCreateSerializer) - для всех.
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadCreateOnly,)
    pagination_class = CustomPageNumberPagination

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
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        me = self.request.user
        serializer = self.get_serializer(me)
        return Response(serializer.data)


class PasswordChangeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для смены пароля.
    Доступ:
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    # def perform_create(self, serializer):
    #     print(f'-------serializer={serializer}\n')
    #     print(f'-------serializer.data={serializer.data}\n')
    #     serializer = ChangePasswordSerializer(data=serializer.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     else:
    #         return Response(serializer.errors,
    #                         status=status.HTTP_400_BAD_REQUEST)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для для просмотра подписок текущего пользователя.
    Доступ:
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = SubscriptionsSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(followed__user=self.request.user)


class SubscribeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для создания/отмены подписки.
    Доступ:
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete', 'post',]

    def perform_create(self, serializer):
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        serializer.save(author=author, user=user)
        return Response('Подписка успешно создана',
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        # author = get_object_or_404(User, id=kwargs.get('pk'))
        try:
            author = User.objects.get(id=kwargs.get('pk'))
        except User.DoesNotExist:
            raise ValidationError('Автор не найден',
                                  code=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(Subscribe, user=user, author=author)
        self.perform_destroy(instance)
        return Response('Успешная отписка', status=status.HTTP_204_NO_CONTENT)


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
    permission_classes = (AllowAny,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    http_method_names = ['get',]


class RecipeViewSet(viewsets.ModelViewSet):
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
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, )
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    # def get_serializer_class(self):
    #     if self.request.method in SAFE_METHODS:
    #         return RecipeSerializer
    #     return RecipeCreateSerializer

    def perform_create(self, serializer):
        print(f'author={self.request.user}')
        serializer.save(author=self.request.user)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """
        Скачать список покупок для выбранных рецептов.
        Доступ:
        Доступно только авторизованному пользователю.
        Авторизация по токену.
        Все запросы от имени пользователя должны выполняться с заголовком
        "Authorization: Token TOKENVALUE".
        """
        user = self.request.user
        if user.shopping_cart.exists():
            return download_cart(self, request, user)
        return Response('Список покупок пуст.',
                        status=status.HTTP_404_NOT_FOUND)


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для добавления/удаления избранного рецепта.
    Доступ:
    Доступно только авторизованному пользователю.
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete', 'post',]

    def perform_create(self, serializer):
        user = self.request.user
        # recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        try:
            recipe = Recipe.objects.get(id=self.kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise ValidationError('Рецепт не найден',
                                  code=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=user, recipe=recipe)
        return Response('Рецепт добавлен в избранное',
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        # recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        try:
            recipe = Recipe.objects.get(id=kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise ValidationError('Рецепт не найден',
                                  code=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(Favorite, user=user, recipe=recipe)
        self.perform_destroy(instance)
        return Response('Рецепт удалён из избранного',
                        status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для добавления/удаления в список покупок.
    Доступ:
    Доступно только авторизованному пользователю.
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete', 'post',]

    def perform_create(self, serializer):
        user = self.request.user
        # recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        try:
            recipe = Recipe.objects.get(id=self.kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise ValidationError('Рецепт не найден',
                                  code=status.HTTP_400_BAD_REQUEST)
        serializer.save(author=user, recipe=recipe)
        return Response('Рецепт добавлен в список покупок',
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        # recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        try:
            recipe = Recipe.objects.get(id=kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise ValidationError('Рецепт не найден',
                                  code=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(ShoppingCart, author=user, recipe=recipe)
        self.perform_destroy(instance)
        return Response('Рецепт удалён из списка покупок',
                        status=status.HTTP_204_NO_CONTENT)
