from django.conf import settings
from django.core.cache import cache

from catalog.models import Product


def get_products_by_category(category_id):
    """Возвращает товары категории, используя низкоуровневый кеш."""
    cache_key = f"category_{category_id}"
    products = cache.get(cache_key)

    if products is None:
        products = list(Product.objects.filter(category_id=category_id))
        cache.set(cache_key, products, timeout=settings.CACHE_TTL)

    return products
