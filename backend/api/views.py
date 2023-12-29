from django.shortcuts import render, get_object_or_404


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для:
    Просмотра собственного профиля пользователя.
    Просмотра своих подписок.
    Подписки на автора рецептов.
    Изменения пароля.
    Доступ:
    - Чтение - для всех.
    - Запись - только автор или администратор.
    """
    queryset = User.objects.all()
    # permission_classes = (IsCurrentUserOrAdminOrReadOnly, )
    # pagination_class = ApiPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=True,)
    def me(self, request):
        """
        Просмотр собственного профиля пользователя.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True,)
    def set_password(self, request, *args, **kwargs):
        """
        Изменение своего пароля.
        Используется встроенный сериалайзер djoser SetPasswordSerializer.
        """
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response(
                'Пароль успешно изменен',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        """
        Создание и удаление подписки.
        """
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data=request.data,
                context={'request': request, 'author': author}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response(
                    {'Подписка успешно создана': serializer.data},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'errors': 'Объект не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        if Subscribe.objects.filter(author=author, user=user).exists():
            Subscribe.objects.get(author=author).delete()
            return Response(
                'Успешная отписка',
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {'errors': 'Объект не найден'},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """
        Отображает все подписки пользователя.
        """
        queryset = self.paginate_queryset(
            Subscribe.objects.filter(user=self.request.user)
        )
        serializer = SubscribeSerializer(
            queryset,
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)
