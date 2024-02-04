# Итоговый проект курса Python-разработчик в Яндекс.Практикум, 68 когорта.

## Проект 
"Foodgram".

## Автор: 
Ефремов Кирилл.

### Описание проекта:

Проект "Foodgram" объединяет любителей кулинарии всего мира.
Здесь зарегистрированные пользователи могут:
- Публиковать и редактировать от своего имени рецепты блюд.
- Подписываться на других авторов рецептов.
- Добавлять себе в избранное понравившиеся рецепты.
- Добавлять рецепты в список покупок и скачивать готовый список в формате *.txt. Одинаковые ингредиенты в списке покупок суммируются.
Незарегистрированным пользователям доступны:
- Просмотр рецептов.
- Просмотр списка пользователей. Вдруг вы увидите здесь своего друга и тоже заходите вступить в клуб?

### Технологии, использованные в проекте:

- Python 3.9.10
- Django 3.2.3
- Djangorestframework 3.12.4
- Djoser 2.1.0
- Docker 4.23.0
- nginx 1.19.3
- Полный перечень зависимостей проекта указан в файле requirement.txt (/foodgram-project-react/backend/foodgram/requirements.txt)

## Техническое описание проекта "Foodgram":
- Фронтенд для проекта разработал и любезно предоставил [Яндекс.Практикум](https://practicum.yandex.ru/).
- Регистрация, авторизация, смена пароля пользователя осуществляются при помощи модуля Djoser.
- Аутентификация пользователя осуществляется по токену, передаваемому в заголовке запроса.
- Проект запускается в контейнерах Docker.

### Ресурсы API "Foodgram":
- "/auth": аутентификация пользователя.
- "/users": список пользователей, выбор определенного автора, регистрация нового пользователя.
- "/users/me": профиль текущего пользователя.
- "/users/set_password": смена пароля текущего пользователя.
- "/users/subscriptions": подписки текущего пользователя на других авторов.
- "/users/<int:pk>/subscribe/": подписка/отписка на автора рецептов.
- "/tags": теги для рецептов. Имеется возможность фильтровать рецепты по тегам. Добавлять новые теги может только администратор
- "/ingredients": ингредиенты для создания рецепта. Фильтруются по названию по началу вхождения. В один рецепт нельзя добавить более одного ингредиента с одинаковым названием. Добавлять новые ингредиенты может только администратор.
- "/recipes": рецепты блюд. Рецепты на главной странице сортируются по дате публикации (более новые впереди), фильтруются по тегам, избранному и списку покупок. Редактирование рецепта доступно только его автору.
- "/recipes/<int:pk>/favorite/": добавить/удалить рецепт в избранное.
- "/recipes/<int:pk>/shopping_cart/": добавить/удалить рецепт в список покупок.
- "/api/docs": документация проекта.

### Документация API:
Документация API доступна по ссылкам:
https://fooagram.hopto.org/api/docs/
http://84.252.141.240/api/docs/

### Пользовательские роли:
Аноним, Аутентифицированный пользователь, Администратор, Автор рецепта.
Роли отдельно не прописаны, определяются логикой проекта.

### Инструкция по запуску проекта:
Проект можно запустить двумя способами: ***локально*** и ***на удалённом сервере***.
*\* На локальной машине или удалённом сервере у Вас должен быть установлен  Docker(для [Windows](https://docs.docker.com/desktop/install/windows-install/), [Linux](https://docs.docker.com/desktop/install/linux-install/), [iOS](https://docs.docker.com/desktop/install/mac-install/), [для удалённого сервера на Ubuntu](https://docs.docker.com/desktop/install/ubuntu/)) версии не ниже 4.23.0 с утилитой **Docker Compose**.*
*\* На удалённом сервере должен быть установлен [nginx](https://nginx.org/ru/docs/install.html) версии не ниже 1.19.3.*

*\*все команды приведены для Windows. При запуске на Linux перед каждой командой нужно добавлять ***sudo***.*

1. Клонируйте проект на Вашу локальную или виртуальную машину.
2. Для удалённого сервера:
Замените содержимое конфигурационного файла nginx на удалённом сервере (**/etc/nginx/sites-enabled/default**) содержимым файла **server_nginx.conf** в каталоге проекта **/foodgram-project-react/infra**. Замените IP-адрес *84.252.141.240* и доменное имя *fooagram.hopto.org* на Ваши. [Обновите](https://dvmn.org/encyclopedia/deploy/renewing-certbot-certificates-for-nginx-using-a-systemd-timer/) SSL сертификаты.
3. Из каталога проекта **foodgram-project-react/infra** выполните комманду:
    - Для локального запуска: `docker compose up -d`
    - Для запуска на удалённом сервере: `docker compose -f docker-compose.production.yml up -d`

4. Дождитесь разворачивания проекта в контейнерах.
5. Последовательно выполните команды:
   `docker compose exec backend bash` (*для локальной машины*)  
   или  
   `docker compose -f docker-compose.production.yml exec backend bash` (*для удалённого сервера*)

   `python manage.py migrate`
   `python manage.py collectstatic`
   `python manage.py createsuperuser`
   *\* заполните необходимые данные для администратора. Запомните <email> и <password>, они будут нужны для входа в админ-зону.*
6. Проверьте работу проекта по ссылке:
   http://127.0.0.1/ (*для локальной машины*)

   *https://<ваше_доменное_имя>* (*для удалённого сервера*)
   или
   *http://<ваш_IP>* 


### Наполнение базы данных:
Для наполнения базы данных подготовленным списком ингредиентов выполните команду:
`docker compose exec backend python manage.py db_import_data` (*для локальной машины*)  
   или  
`docker compose -f docker-compose.production.yml exec backend python manage.py db_import_data` (*для удалённого сервера*)

### Пример запросов/ответов:
Полный перечень запросов и ответов с примерами приведен в документации
http://127.0.0.1/api/docs/ (*для локальной машины*) 

*https://<ваше_доменное_имя>/api/docs/* (*для удалённого сервера*)
или
*http://<ваш_IP>/api/docs/*

Пример запроса для создания рецепта: **POST** запрос на адрес http://127.0.0.1/api/recipes/

**Неавторизованный пользователь:**
***Request:***

```
{
"ingredients": [
{
"id": 1,
"amount": 1000
}
],
"tags": [2,3],
"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
"name": "Test_recipe",
"text": "Test_test_test",
"cooking_time": 10
}
```

***Response:***

```
{
    "detail": "Authentication credentials were not provided."
}
```

**Авторизованный пользователь:**
***Request:***

```
{
"ingredients": [
{
"id": 1,
"amount": 1000
}
],
"tags": [2,3],
"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
"name": "Test_recipe",
"text": "Test_test_test",
"cooking_time": 10
}
```

***Response:***

```
{
    "id": 73,
    "tags": [
        {
            "id": 2,
            "name": "Обед",
            "color": "Зеленый",
            "slug": "lunch"
        },
        {
            "id": 3,
            "name": "Ужин",
            "color": "Синий",
            "slug": "dinner"
        }
    ],
    "author": {
        "email": "halo@2season.com",
        "id": 1,
        "username": "MasterChief",
        "first_name": "John",
        "last_name": "John",
        "is_subscribed": false
    },
    "ingredients": [
        {
            "id": 1,
            "name": "абрикосовое варенье",
            "measurement_unit": "г",
            "amount": 1000
        }
    ],
    "is_favorited": false,
    "is_in_shopping_cart": false,
    "name": "Test_recipe",
    "image": "http://127.0.0.1:8000/media/recipes_img/482d9d29-f5d1-4e60-8386-fb75ac42f06e.png",
    "text": "Test_test_test",
    "cooking_time": 10
}
```


# Информация для проверки проекта:
Адрес сервера: https://fooagram.hopto.org/
IP сервера: https://84.252.141.240/

Логин суперюзера: admin@admin.ad
Пароль суперюзера: admin
