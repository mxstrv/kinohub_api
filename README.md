# Kinohub REST API (pet-project)

## Описание
Kinohub - Cервис с обзорами фильмов, их рейтингами, комментариями. Реализован полностью функционирующий бэкенд на django rest framework.
### Зависимости
Для работоспособности необходимые следующие библиотеки:
>requests 2.31.0  
Django 3.2.20    
djangorestframework 3.12.4  
PyJWT 2.1.0  
django-filter 22.1
djangorestframework 3.12.4  


### Установка
Клонируйте репозиторий коммандой `git clone git@github.com:mxstrv/kinohub_api.git`

Создайте виртуальное окружение   `python3 -m venv venv`

Активируйте виртуальное окружение `source venv/bin/activate`(для Linux и MacOS) `source venv/Scripts/activate` (для Windows)

Установите зависимости `pip install -r requirements.txt`

Выполните миграции `python manage.py makemigration && python manage.py migrate`

Запустите сервер `python manage.py runserver`

### Описание и примеры запросов
### Регистрация пользователя
Для регистрации пользователя необходимо отправить POST запрос на URL `http://127.0.0.1:8000/api/v1/auth/signup/`
в формате 
>`{
"email": "user@example.com",
"username": "username"
}`
> 
Затем на e-mail придет код подтверждения. Его, и e-mail, необходимо отправить POST запросом на URL`http://127.0.0.1:8000/api/v1/auth/token/`
в формате
>`{
"username": "username", "confirmation_code": "code"
}`
> 
В ответе будет JWT токен, необходимый для взаимодействия с web-приложением (Вставляется в формате Bearer "token")
### Работа с пользователями
Пользователю с правами администратора доступно полное взаимодействие с пользователями, а именно:
* Регистрация новых пользователей
* Удаление пользователей
* Изменение их данных, в т.ч. добавление ролей модератора или администратора
* Пользователь может найти информацию о себе по URL `http://127.0.0.1:8000/api/v1/users/me/`

### Документация OpenAPI
Подробная документация по проекту c использованием спецификации OpenAPI доступна по адресу http://127.0.0.1:8000/redoc/
