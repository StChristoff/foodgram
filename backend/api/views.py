from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnly, ReadOrCreateOnly
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
      Просмотр списка авторов.
      Просмотр профиля автора.
    Доступ:
    - Просмотр списка и профиля авторов (UserSerializer) - для всех.
    - Создание пользователя (UserCreateSerializer) - для всех.
    """
    queryset = User.objects.all()
    permission_classes = (ReadOrCreateOnly,)
    pagination_class = CustomPageNumberPagination
    http_method_names = ['get', 'post', ]

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
    http_method_names = ['delete', 'post', ]

    def perform_create(self, serializer):
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        serializer.save(author=author, user=user)
        return Response('Подписка успешно создана',
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=kwargs.get('pk'))
        try:
            instance = Subscribe.objects.get(user=user, author=author)
        except Subscribe.DoesNotExist:
            raise ValidationError({'errors': 'Нет подписки на этого автора'},
                                  code=status.HTTP_400_BAD_REQUEST)
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
    http_method_names = ['get', ]


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
    http_method_names = ['get', ]


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для:
    - Получения списка рецептов.
    - Получения отдельного рецепта.
    - Создания рецепта.
    - Редактирования рецепта.
    - Удаления рецепта.
    Доступ:
    - Чтение - для всех.
    - Запись:
      - Создание рецепта - аутентифицированный пользователь.
      - Редактирование и удаление рецепта - только автор.
    """
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, )
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
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
    Вьюсет для добавления/удаления рецепта в избранное.
    Доступ:
    Доступно только авторизованному пользователю.
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete', 'post', ]

    def perform_create(self, serializer):
        user = self.request.user
        try:
            recipe = Recipe.objects.get(id=self.kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise ValidationError({'errors': 'Рецепт не найден'},
                                  code=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=user, recipe=recipe)
        return Response('Рецепт добавлен в избранное',
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        try:
            instance = Favorite.objects.get(user=user, recipe=recipe)
        except Favorite.DoesNotExist:
            raise ValidationError({'errors': 'Этот рецепт не в избранном'},
                                  code=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response('Рецепт удалён из избранного',
                        status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для добавления/удаления рецепта в список покупок.
    Доступ:
    Доступно только авторизованному пользователю.
    Авторизация по токену.
    Все запросы от имени пользователя должны выполняться с заголовком
    "Authorization: Token TOKENVALUE".
    """
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ['delete', 'post', ]

    def perform_create(self, serializer):
        user = self.request.user
        try:
            recipe = Recipe.objects.get(id=self.kwargs.get('pk'))
        except Recipe.DoesNotExist:
            raise ValidationError({'errors': 'Рецепт не найден'},
                                  code=status.HTTP_400_BAD_REQUEST)
        serializer.save(author=user, recipe=recipe)
        return Response('Рецепт добавлен в список покупок',
                        status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        try:
            instance = ShoppingCart.objects.get(author=user, recipe=recipe)
        except ShoppingCart.DoesNotExist:
            raise ValidationError({'errors': 'Этот рецепт '
                                   'не в списке покупок'},
                                  code=status.HTTP_400_BAD_REQUEST)
        self.perform_destroy(instance)
        return Response('Рецепт удалён из списка покупок',
                        status=status.HTTP_204_NO_CONTENT)
