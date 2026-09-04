from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import Blog
from catalog.models import Product


class Command(BaseCommand):
    """Создаёт учебные группы и назначает им необходимые права."""

    help = "Создаёт группы модераторов продуктов и контент-менеджеров."

    def handle(self, *args, **options):
        product_content_type = ContentType.objects.get_for_model(Product)
        product_permissions = Permission.objects.filter(
            content_type=product_content_type,
            codename__in=(
                "can_unpublish_product",
                "change_product",
                "delete_product",
            ),
        )

        product_moderators, _ = Group.objects.get_or_create(
            name="Модератор продуктов"
        )
        product_moderators.permissions.set(product_permissions)

        blog_content_type = ContentType.objects.get_for_model(Blog)
        blog_permissions = Permission.objects.filter(
            content_type=blog_content_type,
            codename__in=(
                "add_blog",
                "change_blog",
                "delete_blog",
            ),
        )

        content_managers, _ = Group.objects.get_or_create(
            name="Контент-менеджер"
        )
        content_managers.permissions.set(blog_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                "Группы «Модератор продуктов» и «Контент-менеджер» настроены."
            )
        )
