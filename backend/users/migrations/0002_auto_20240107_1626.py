# Generated by Django 3.2.6 on 2024-01-07 13:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscribe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(help_text='Выберите Автора рецептов', on_delete=django.db.models.deletion.CASCADE, related_name='followed', to=settings.AUTH_USER_MODEL, verbose_name='Подписка')),
                ('user', models.ForeignKey(help_text='Выберите Пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Подписка на пользователя',
                'verbose_name_plural': 'Подписки на пользователей',
            },
        ),
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='Уникальная пара: Подписчик-Автор'),
        ),
    ]
