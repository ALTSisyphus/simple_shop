# Скриншоты работы с Django Shell

Сначала примените миграции, затем откройте интерактивную оболочку:

```bash
poetry run python manage.py migrate
poetry run python manage.py shell
```

Выполняйте блоки по порядку. После каждого блока сделайте настоящий скриншот,
на котором видны введённые команды и результат.

## 1. Создание категорий

```python
from catalog.models import Category, Product
from decimal import Decimal

mailing = Category.objects.create(name="Рассылки", description="Сервисы рассылок")
bots = Category.objects.create(name="Телеграм-боты", description="Боты для Telegram")
mailing, bots
```

Должны отобразиться две созданные категории. Имя файла:
`01_create_categories.png`.

## 2. Создание продуктов

```python
service = Product.objects.create(name="Сервис рассылок", description="Автоматизация писем", category=mailing, price=Decimal("140.00"))
support_bot = Product.objects.create(name="Бот поддержки", description="Ответы клиентам", category=bots, price=Decimal("89.90"))
service, support_bot
```

Должны отобразиться два продукта. Изображение не передаётся, поскольку оно
необязательно. Имя файла: `02_create_products.png`.

## 3. Получение всех объектов

```python
Category.objects.all()
Product.objects.all()
```

Должны быть видны обе категории и оба продукта. Имя файла: `03_get_all.png`.

## 4. Фильтрация по категории

```python
Product.objects.filter(category=mailing)
```

В результате должен остаться продукт «Сервис рассылок». Имя файла:
`04_filter_products.png`.

## 5. Обновление цены

```python
service.price = Decimal("149.90")
service.save()
Product.objects.get(pk=service.pk).price
```

Должна отобразиться новая цена `Decimal('149.90')`. Имя файла:
`05_update_price.png`.

## 6. Удаление продукта

```python
support_bot.delete()
Product.objects.all()
```

В списке должен остаться только «Сервис рассылок». Имя файла:
`06_delete_product.png`.

Не добавляйте постановочные или отредактированные изображения: скриншоты должны
показывать фактический результат выполнения команд в вашем окружении.
