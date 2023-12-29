from django.db import models
from django.contrib.auth.models import AbstractUser

from foodgram.settings import USERNAME_LEN, EMAIL_LEN, F_S_NAME_LEN, PASS_LEN


class User(AbstractUser):
    """
    Создаёт пользовательский класс User.
    """
    email = models.EmailField(
        verbose_name='Email',
        max_length=EMAIL_LEN,
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
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=F_S_NAME_LEN,
        help_text="Введите Ваше Имя"
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=F_S_NAME_LEN,
        help_text="Введите Вашу Фамилию",
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=PASS_LEN,
        help_text="Придумайте пароль",
    )
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

