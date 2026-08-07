from django.contrib import admin

from blog.models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    """Настройки отображения блоговых записей в административной панели."""

    list_display = (
        "id",
        "title",
        "created_at",
        "is_published",
        "views_count",
    )
    list_filter = (
        "is_published",
        "created_at",
    )
    search_fields = (
        "title",
        "content",
    )
    readonly_fields = (
        "created_at",
        "views_count",
    )
