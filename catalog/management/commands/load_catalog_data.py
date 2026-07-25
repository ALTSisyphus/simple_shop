from django.core.management import BaseCommand, CommandError, call_command
from django.db import transaction

from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Очищает каталог и загружает тестовые данные из фикстуры."

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                Product.objects.all().delete()
                Category.objects.all().delete()
                call_command("loaddata", "catalog_data.json", verbosity=0)
        except Exception as error:
            raise CommandError(f"Не удалось загрузить данные каталога: {error}") from error

        self.stdout.write(
            self.style.SUCCESS("Тестовые данные каталога успешно загружены.")
        )
