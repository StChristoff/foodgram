from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        SAFE_METHODS)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomUserSerializer, SubscriptionsSerializer,
                          SubscribeSerializer, TagSerializer,
                          IngredientSerializer, RecipeGetSerializer,
                          RecipeCreateSerializer,
                          FavoriteSerializer, ShoppingCartSerializer)
from recipes.models import (Tag, Ingredient, Recipe, Favorite, ShoppingCart,
                            IngredientRecipe)
from users.models import User, Subscribe


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для:
      Просмотр списка авторов.
      Просмотр профиля автора (по id).
      Просмотр текущего пользователя (users/me/, реализовано на Djoser).
      Создание пользователя (POST запрос).
      Получение токена (auth/token/login/, реализовано на Djoser).
      Смена пароля пользователя (users/set_password/, реализовано на Djoser).
      Получение списка подписок текущего пользователя (users/subscriptions/).
      Создание и удаление подписки на автора (users/<int:id>/subscribe/).

    Доступ:
    - Просмотр списка и профиля авторов (UserSerializer) - для всех.
    - Создание пользователя (UserCreateSerializer) - для всех.
    """
    queryset = User.objects.all()
    pagination_class = CustomPageNumberPagination
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated(), ]
        return super().get_permissions()

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """
        Метод для для просмотра подписок текущего пользователя.
        Доступ:
        Авторизация по токену.
        Все запросы от имени пользователя должны выполняться с заголовком
        "Authorization: Token TOKENVALUE".
        """
        followed = User.objects.filter(followed__user=self.request.user)
        pages = self.paginate_queryset(followed)
        serializer = SubscriptionsSerializer(pages,
                                             many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        """
        Метод для создания/отмены подписки.
        Доступ:
        Авторизация по токену.
        Все запросы от имени пользователя должны выполняться с заголовком
        "Authorization: Token TOKENVALUE".
        """
        user = self.request.user
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if request.method == 'POST':
            serializer = SubscribeSerializer(data={'user': user.id,
                                                   'author': author.id},
                                             context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(author=author, user=user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        delete_cnt, _ = Subscribe.objects.filter(user=user,
                                                 author=author).delete()
        if not delete_cnt:
            return Response({'errors': 'Нет подписки на этого автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response('Успешная отписка',
                        status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
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


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
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
    permission_classes = (IsAuthorOrReadOnly, )
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeGetSerializer
        return RecipeCreateSerializer

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """
        Скачать список покупок для выбранных рецептов.
        Файл в формате txt.
        Доступ:
        Доступно только авторизованному пользователю.
        Авторизация по токену.
        Все запросы от имени пользователя должны выполняться с заголовком
        "Authorization: Token TOKENVALUE".
        """
        user = self.request.user
        if user.shopping_cart.exists():
            ingredients_sum = IngredientRecipe.objects.filter(
                recipe__shopping_cart__author=user
            ).values(
                'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(amounts=Sum('amount')).order_by('ingredient__name')

            text = f'Список покупок ({user.first_name} {user.last_name})\n\n'
            for ingredient in ingredients_sum:
                text += (f'{ingredient["ingredient__name"]} - '
                         f'{ingredient["amounts"]} '
                         f'{ingredient["ingredient__measurement_unit"]}\n')

            file_name = f'Shopping_cart_{user.first_name}_{user.last_name}.txt'
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = (
                f'attachment; filename="{file_name}"')
            response.write(text)
            return response
        return Response('Список покупок пуст.',
                        status=status.HTTP_404_NOT_FOUND)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, *args, **kwargs):
        """
        Метод для добавления/удаления рецепта в избранное.
        Доступ:
        Доступно только авторизованному пользователю.
        Авторизация по токену.
        Все запросы от имени пользователя должны выполняться с заголовком
        "Authorization: Token TOKENVALUE".
        """
        user = self.request.user
        if request.method == 'POST':
            serializer = FavoriteSerializer(data={'user': user.id,
                                                  'recipe': kwargs.get('pk')},
                                            context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
        delete_cnt, _ = Favorite.objects.filter(user=user,
                                                recipe=recipe).delete()
        if not delete_cnt:
            return Response({'errors': 'Этот рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response('Рецепт удалён из избранного',
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, **kwargs):
        """
        Вьюсет для добавления/удаления рецепта в список покупок.
        Доступ:
        Доступно только авторизованному пользователю.
        Авторизация по токену.
        Все запросы от имени пользователя должны выполняться с заголовком
        "Authorization: Token TOKENVALUE".
        """
        user = self.request.user
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'author': user.id,
                      'recipe': kwargs.get('pk')},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        delete_cnt, _ = ShoppingCart.objects.filter(author=user,
                                                    recipe=recipe).delete()
        if not delete_cnt:
            return Response({'errors': 'Этот рецепт не в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response('Рецепт удалён из списка покупок',
                        status=status.HTTP_204_NO_CONTENT)
