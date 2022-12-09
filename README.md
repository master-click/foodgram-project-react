# «Продуктовый помощник» Foodgram

## Что умеет Foodgram

Все пользователи могут посмотреть рецепты, зарегистрироваться на сайте, чтобы:
- публиковать свои рецепты;
- подписываться на публикации других зарегистрированных пользователей;
- добавлять понравившиеся рецепты в список «Избранное»;
- создавать и скачивать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Стэк технологий

- Python;
- Django;
- Django Rest Framework;
- PostgreSQL;
- Docker;

## Запуск проекта на сервере

1. Клонируем проект:

```
git clone git@github.com:master-click/foodgram-project-react.git
```

2. Устанавливаем docker на сервере:

```
sudo apt install docker.io 
sudo apt install docker-compose
```

3. Собираем контейнер:

```
sudo docker-compose up -d --build
```

4. Выполняем миграции, создаем суперпользователя, добавляем статику и загружаем базу ингредиентов:

```
sudo docker exec -it <CONTAINER ID> bash # Заходим внутрь контейнера
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py loaddata ingredients.json
exit # Выходим из контейнера
```

## Данные для проверки проекта

```
email: master-click@yandex.ru
password: admin
```

### Разработчик
Батова Ольга, @olgabato