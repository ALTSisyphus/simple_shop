# Skystore

Skystore — учебный проект интернет-магазина на Django.

## Описание

Проект содержит приложение `catalog` с двумя страницами:

- главная страница каталога по адресу `/`;
- страница контактов с формой обратной связи по адресу `/contacts/`.

Страницы сверстаны на HTML с использованием Bootstrap.

## Структура проекта

```text
simple_shop/
├── catalog/
│   ├── templates/
│   │   └── catalog/
│   │       ├── home.html
│   │       └── contacts.html
│   ├── fixtures/
│   ├── management/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── screenshots/
├── requirements.txt
├── .gitignore
└── README.md
```
