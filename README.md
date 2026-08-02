# Skystore

Skystore — учебный интернет-магазин на Django с каталогом товаров и блогом.
Проект использует Django, PostgreSQL, Poetry, Bootstrap и Pillow.

## Возможности каталога

В приложении `catalog` реализованы:

- список товаров с пагинацией по шесть карточек;
- детальная страница товара;
- создание, редактирование и удаление товара через class-based views;
- единая `ProductForm` на основе `ModelForm` для создания и редактирования;
- автоматическое назначение категории «Без категории» только новым товарам;
- серверная проверка запрещённых слов в названии и описании без учёта регистра;
- запрет отрицательной цены при разрешённых нулевых и положительных значениях;
- загрузка только фактических JPEG/PNG изображений размером не более 5 МБ;
- Bootstrap-стилизация полей формы через `ProductForm.__init__`;
- страница контактов и форма обратной связи.

Маршруты CRUD:

- `/` — список товаров;
- `/products/create/` — создание;
- `/products/<pk>/` — просмотр;
- `/products/<pk>/edit/` — редактирование;
- `/products/<pk>/delete/` — подтверждение удаления.

## Возможности блога

В приложении `blog` реализован полный CRUD записей через CBV. В списке
отображаются только опубликованные статьи, поддерживаются превью, счётчик
просмотров и Bootstrap-оформление формы, включая чекбокс публикации.

## Подготовка окружения

Требуются Python, PostgreSQL и Poetry. Создайте локальный `.env` на основе
`.env.example` и укажите параметры своей базы данных. Не добавляйте `.env` в
репозиторий.

```bash
cp .env.example .env
poetry install --no-root
poetry run python manage.py migrate
```

Загрузка демонстрационных данных при необходимости:

```bash
poetry run python manage.py load_catalog_data
```

## Запуск

```bash
poetry run python manage.py runserver
```

После запуска проект доступен по адресу `http://127.0.0.1:8000/`.

## Проверки и тесты

```bash
poetry run python manage.py check
poetry run python manage.py makemigrations --check --dry-run
poetry run python manage.py test
```

При работе в уже активированном виртуальном окружении команды можно запускать
без префикса `poetry run`:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```
