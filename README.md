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

4. Выполняем миграции и добавляем статику:

```
sudo docker-compose exec foodgram-backend python manage.py makemigrations
sudo docker-compose exec foodgram-backend python manage.py migrate
sudo docker-compose exec foodgram-backend python manage.py collectstatic
```

5. Загружаем данные из дампа базы данных:

```
sudo docker-compose exec foodgram-backend loaddata > dump.json
```

### Разработчик ###
Батова Ольга, @olgabato