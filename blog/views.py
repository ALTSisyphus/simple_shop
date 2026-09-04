from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.forms import BlogForm
from blog.models import Blog


class BlogListView(ListView):
    """Отображает список опубликованных блоговых записей."""

    model = Blog
    template_name = "blog/blog_list.html"
    context_object_name = "blogs"

    def get_queryset(self):
        """Возвращает только опубликованные блоговые записи."""
        return Blog.objects.filter(is_published=True)


class BlogDetailView(DetailView):
    """Отображает отдельную блоговую запись."""

    model = Blog
    template_name = "blog/blog_detail.html"
    context_object_name = "blog"

    def get_object(self, queryset=None):
        """Получает статью и увеличивает счётчик её просмотров."""
        blog = super().get_object(queryset)
        blog.views_count += 1
        blog.save(update_fields=("views_count",))

        return blog


class BlogCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Создаёт запись пользователем с правом управления блогом."""

    model = Blog
    form_class = BlogForm
    template_name = "blog/blog_form.html"
    permission_required = "blog.add_blog"

    def get_success_url(self):
        """Перенаправляет на созданную блоговую запись."""
        return reverse_lazy(
            "blog:blog_detail",
            kwargs={"pk": self.object.pk},
        )


class BlogUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Редактирует запись пользователем с правом изменения блога."""

    model = Blog
    form_class = BlogForm
    template_name = "blog/blog_form.html"
    permission_required = "blog.change_blog"

    def get_success_url(self):
        """Перенаправляет на отредактированную блоговую запись."""
        return reverse_lazy(
            "blog:blog_detail",
            kwargs={"pk": self.object.pk},
        )


class BlogDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Удаляет запись пользователем с правом удаления блога."""

    model = Blog
    template_name = "blog/blog_confirm_delete.html"
    success_url = reverse_lazy("blog:blog_list")
    permission_required = "blog.delete_blog"
