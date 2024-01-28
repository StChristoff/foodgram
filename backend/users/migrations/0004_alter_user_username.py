# Generated by Django 3.2.6 on 2024-01-28 22:08

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_subscribe_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(help_text='Введите Псевдоним (не более 150 символов). Допускаются буквы, цифры, символы @/./+/-/_ .', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator], verbose_name='Псевдоним'),
        ),
    ]
