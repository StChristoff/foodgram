# Generated by Django 3.2.3 on 2024-01-11 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20240109_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(help_text='Выберите Тег', to='recipes.Tag', verbose_name='Тег'),
        ),
    ]
