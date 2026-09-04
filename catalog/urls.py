from django.conf import settings
from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from catalog.apps import CatalogConfig
from catalog.views import (
    CategoryProductListView,
    ContactsView,
    ProductCreateView,
    ProductDeleteView,
    ProductDetailView,
    ProductListView,
    ProductUnpublishView,
    ProductUpdateView,
)

app_name = CatalogConfig.name


cached_product_detail_view = cache_page(settings.CACHE_TTL)(
    vary_on_cookie(ProductDetailView.as_view())
)

urlpatterns = [
    path(
        "",
        ProductListView.as_view(),
        name="home",
    ),
    path(
        "contacts/",
        ContactsView.as_view(),
        name="contacts",
    ),
    path(
        "products/create/",
        ProductCreateView.as_view(),
        name="product_create",
    ),
    path(
        "products/<int:pk>/",
        cached_product_detail_view,
        name="product_detail",
    ),
    path(
        "categories/<int:category_id>/",
        CategoryProductListView.as_view(),
        name="category_products",
    ),
    path(
        "products/<int:pk>/edit/",
        ProductUpdateView.as_view(),
        name="product_update",
    ),
    path(
        "products/<int:pk>/delete/",
        ProductDeleteView.as_view(),
        name="product_delete",
    ),
    path(
        "products/<int:pk>/unpublish/",
        ProductUnpublishView.as_view(),
        name="product_unpublish",
    ),
]
