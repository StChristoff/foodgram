from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
# from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnly, ReadOrCreateOnly
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
            return [IsAuthenticated(),]
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
        if pages is not None:
            serializer = SubscriptionsSerializer(pages,
                                                 many=True,
                                                 context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(followed, many=True)
        return Response(serializer.data)

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
            serializer = SubscribeSerializer(
                data=request.data,
                context={'request': request, 'author': author})
            if serializer.is_valid():
                serializer.save(author=author, user=user)
                return Response({'Подписка успешно создана': serializer.data},
                                status=status.HTTP_201_CREATED)
        delete_cnt, _ = Subscribe.objects.filter(user=user,
                                                 author=author).delete()
        if not delete_cnt:
            return Response({'errors': 'Нет подписки на этого автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response('Успешная отписка',
                        status=status.HTTP_204_NO_CONTENT)
    
        # try:
        #     Subscribe.objects.get(user=user, author=author).delete()
        #     return Response('Успешная отписка',
        #                     status=status.HTTP_204_NO_CONTENT)
        # except Subscribe.DoesNotExist:
        #     raise ValidationError({'errors': 'Нет подписки на этого автора'},
        #                           code=status.HTTP_400_BAD_REQUEST)
    
# class UserViewSet(viewsets.ModelViewSet):
#     """
#     Вьюсет для:
#     - UserCreateSerializer: Создание пользователя
#     - UserSerializer:
#       Просмотр списка авторов.
#       Просмотр профиля автора.
#     Доступ:
#     - Просмотр списка и профиля авторов (UserSerializer) - для всех.
#     - Создание пользователя (UserCreateSerializer) - для всех.
#     """
#     queryset = User.objects.all()
#     permission_classes = (ReadOrCreateOnly,)
#     pagination_class = CustomPageNumberPagination
#     http_method_names = ['get', 'post', ]

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return UserCreateSerializer
#         return UserSerializer


# class UserMeViewSet(viewsets.ModelViewSet):
#     """
#     Вьюсет для просмотра собственного профиля.
#     Доступ:
#     Авторизация по токену.
#     Все запросы от имени пользователя должны выполняться с заголовком
#     "Authorization: Token TOKENVALUE".
#     """
#     serializer_class = UserSerializer
#     permission_classes = (IsAuthenticated,)

#     def list(self, request, *args, **kwargs):
#         me = self.request.user
#         serializer = self.get_serializer(me)
#         return Response(serializer.data)


# class PasswordChangeViewSet(viewsets.ModelViewSet):
#     """
#     Вьюсет для смены пароля.
#     Доступ:
#     Авторизация по токену.
#     Все запросы от имени пользователя должны выполняться с заголовком
#     "Authorization: Token TOKENVALUE".
#     """
#     serializer_class = ChangePasswordSerializer
#     permission_classes = (IsAuthenticated,)


# class SubscriptionsViewSet(viewsets.ModelViewSet):
#     """
#     Вьюсет для для просмотра подписок текущего пользователя.
#     Доступ:
#     Авторизация по токену.
#     Все запросы от имени пользователя должны выполняться с заголовком
#     "Authorization: Token TOKENVALUE".
#     """
#     serializer_class = SubscriptionsSerializer
#     pagination_class = CustomPageNumberPagination
#     permission_classes = (IsAuthenticated,)

#     def get_queryset(self):
#         return User.objects.filter(followed__user=self.request.user)


# class SubscribeViewSet(viewsets.ModelViewSet):
#     """
#     Вьюсет для создания/отмены подписки.
#     Доступ:
#     Авторизация по токену.
#     Все запросы от имени пользователя должны выполняться с заголовком
#     "Authorization: Token TOKENVALUE".
#     """
#     serializer_class = SubscribeSerializer
#     permission_classes = (IsAuthenticated,)
#     http_method_names = ['delete', 'post', ]

#     def perform_create(self, serializer):
#         user = self.request.user
#         author = get_object_or_404(User, id=self.kwargs.get('pk'))
#         serializer.save(author=author, user=user)
#         return Response('Подписка успешно создана',
#                         status=status.HTTP_201_CREATED)

#     def destroy(self, request, *args, **kwargs):
#         user = self.request.user
#         author = get_object_or_404(User, id=kwargs.get('pk'))
#         try:
#             instance = Subscribe.objects.get(user=user, author=author)
#         except Subscribe.DoesNotExist:
#             raise ValidationError({'errors': 'Нет подписки на этого автора'},
#                                   code=status.HTTP_400_BAD_REQUEST)
#         self.perform_destroy(instance)
#         return Response('Успешная отписка', status=status.HTTP_204_NO_CONTENT)


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
    # serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly, )
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

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
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        if request.method == 'POST':
            serializer = FavoriteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user, recipe=recipe)
                return Response(
                    {'Рецепт добавлен в избранное': serializer.data},
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
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
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('id'))
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=user, recipe=recipe)
                return Response(
                    {'Рецепт добавлен в список покупок': serializer.data},
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        delete_cnt, _ = ShoppingCart.objects.filter(author=user,
                                                    recipe=recipe).delete()
        if not delete_cnt:
            return Response({'errors': 'Этот рецепт не в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response('Рецепт удалён из списка покупок',
                        status=status.HTTP_204_NO_CONTENT)


# class FavoriteViewSet(viewsets.ModelViewSet):
#     """
#     Вьюсет для добавления/удаления рецепта в избранное.
#     Доступ:
#     Доступно только авторизованному пользователю.
#     Авторизация по токену.
#     Все запросы от имени пользователя должны выполняться с заголовком
#     "Authorization: Token TOKENVALUE".
#     """
#     serializer_class = FavoriteSerializer
#     permission_classes = (IsAuthenticated,)
#     http_method_names = ['delete', 'post', ]

#     def perform_create(self, serializer):
#         user = self.request.user
#         try:
#             recipe = Recipe.objects.get(id=self.kwargs.get('pk'))
#         except Recipe.DoesNotExist:
#             raise ValidationError({'errors': 'Рецепт не найден'},
#                                   code=status.HTTP_400_BAD_REQUEST)
#         serializer.save(user=user, recipe=recipe)
#         return Response('Рецепт добавлен в избранное',
#                         status=status.HTTP_201_CREATED)

#     def destroy(self, request, *args, **kwargs):
#         user = self.request.user
#         recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
#         try:
#             instance = Favorite.objects.get(user=user, recipe=recipe)
#         except Favorite.DoesNotExist:
#             raise ValidationError({'errors': 'Этот рецепт не в избранном'},
#                                   code=status.HTTP_400_BAD_REQUEST)
#         self.perform_destroy(instance)
#         return Response('Рецепт удалён из избранного',
#                         status=status.HTTP_204_NO_CONTENT)


# class ShoppingCartViewSet(viewsets.ModelViewSet):
#     """
#     Вьюсет для добавления/удаления рецепта в список покупок.
#     Доступ:
#     Доступно только авторизованному пользователю.
#     Авторизация по токену.
#     Все запросы от имени пользователя должны выполняться с заголовком
#     "Authorization: Token TOKENVALUE".
#     """
#     serializer_class = ShoppingCartSerializer
#     permission_classes = (IsAuthenticated,)
#     http_method_names = ['delete', 'post', ]

#     def perform_create(self, serializer):
#         user = self.request.user
#         try:
#             recipe = Recipe.objects.get(id=self.kwargs.get('pk'))
#         except Recipe.DoesNotExist:
#             raise ValidationError({'errors': 'Рецепт не найден'},
#                                   code=status.HTTP_400_BAD_REQUEST)
#         serializer.save(author=user, recipe=recipe)
#         return Response('Рецепт добавлен в список покупок',
#                         status=status.HTTP_201_CREATED)

#     def destroy(self, request, *args, **kwargs):
#         user = self.request.user
#         recipe = get_object_or_404(Recipe, id=kwargs.get('pk'))
#         try:
#             instance = ShoppingCart.objects.get(author=user, recipe=recipe)
#         except ShoppingCart.DoesNotExist:
#             raise ValidationError({'errors': 'Этот рецепт '
#                                    'не в списке покупок'},
#                                   code=status.HTTP_400_BAD_REQUEST)
#         self.perform_destroy(instance)
#         return Response('Рецепт удалён из списка покупок',
#                         status=status.HTTP_204_NO_CONTENT)
