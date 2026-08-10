from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from catalog.forms import ProductForm
from catalog.models import Category, Contact, Product
from catalog.services import get_products_by_category


class ProductOwnerOrPermissionMixin(UserPassesTestMixin):
    """Разрешает действие владельцу товара или пользователю с правом."""

    permission_required = None

    def test_func(self):
        product = self.get_object()
        is_owner = product.owner_id == self.request.user.pk
        has_permission = self.request.user.has_perm(self.permission_required)
        return is_owner or has_permission


class ProductListView(ListView):
    """Отображает главную страницу с постраничным списком товаров."""

    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6


class CategoryProductListView(ListView):
    """Отображает список всех товаров выбранной категории."""

    template_name = "catalog/category_products.html"
    context_object_name = "products"

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            pk=self.kwargs["category_id"],
        )
        return get_products_by_category(self.category.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Отображает подробную информацию о выбранном товаре."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class ProductCreateView(LoginRequiredMixin, CreateView):
    """Создаёт новый товар через форму."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def form_valid(self, form):
        """Назначает владельца и категорию по умолчанию новому товару."""
        category, _ = Category.objects.get_or_create(
            name="Без категории",
            defaults={
                "description": "Товары, добавленные через форму.",
            },
        )
        form.instance.category = category
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет на страницу созданного товара."""
        return reverse(
            "catalog:product_detail",
            kwargs={"pk": self.object.pk},
        )


class ProductUpdateView(
    LoginRequiredMixin,
    ProductOwnerOrPermissionMixin,
    UpdateView,
):
    """Редактирует товар владельца или пользователя с правом изменения."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    permission_required = "catalog.change_product"

    def get_success_url(self):
        """Перенаправляет на страницу изменённого товара."""
        return reverse(
            "catalog:product_detail",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(
    LoginRequiredMixin,
    ProductOwnerOrPermissionMixin,
    DeleteView,
):
    """Удаляет товар владельца или пользователя с правом удаления."""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:home")
    permission_required = "catalog.delete_product"


class ProductUnpublishView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    View,
):
    """Отменяет публикацию товара при наличии специального права."""

    permission_required = "catalog.can_unpublish_product"

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        if product.is_published:
            product.is_published = False
            product.save(update_fields=("is_published",))

        return redirect("catalog:product_detail", pk=product.pk)


class ContactsView(View):
    """Отображает контакты и обрабатывает форму обратной связи."""

    template_name = "catalog/contacts.html"

    def get(self, request):
        """Отображает страницу контактов."""
        return render(
            request,
            self.template_name,
            {
                "success_message": None,
                "contacts": Contact.objects.all(),
            },
        )

    def post(self, request):
        """Обрабатывает отправленную форму обратной связи."""
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        print("Получено сообщение обратной связи:")
        print(f"Имя: {name}")
        print(f"Телефон: {phone}")
        print(f"Сообщение: {message}")

        return render(
            request,
            self.template_name,
            {
                "success_message": "Сообщение успешно отправлено!",
                "contacts": Contact.objects.all(),
            },
        )
