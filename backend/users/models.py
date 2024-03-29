from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator

from foodgram.constants import (USERNAME_LEN, FIRST_NAME_LEN,
                                LAST_NAME_LEN, PASS_LEN)


class User(AbstractUser):
    """
    Custom-Модель User'a.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        help_text="Введите адрес электронной почты.",
    )
    username = models.CharField(
        verbose_name='Псевдоним',
        max_length=USERNAME_LEN,
        unique=True,
        help_text=(
            f'Введите Псевдоним (не более {USERNAME_LEN} символов). '
            f'Допускаются буквы, цифры, символы @/./+/-/_ .'
        ),
        validators=[UnicodeUsernameValidator()],
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=FIRST_NAME_LEN,
        help_text="Введите Ваше Имя"
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=LAST_NAME_LEN,
        help_text="Введите Вашу Фамилию",
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=PASS_LEN,
        help_text="Придумайте пароль",
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """
    Подписка на авторов рецептов.
    """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='follower',
        help_text='Выберите Пользователя',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Подписка',
        on_delete=models.CASCADE,
        related_name='followed',
        help_text='Выберите Автора рецептов',
    )

    class Meta:
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Уникальная пара: Подписчик-Автор'),
        ]

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'
