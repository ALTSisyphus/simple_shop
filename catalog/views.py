from django.shortcuts import render
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


class ProductListView(ListView):
    """Отображает главную страницу с постраничным списком товаров."""

    model = Product
    template_name = "catalog/home.html"
    context_object_name = "products"
    paginate_by = 6


class ProductDetailView(DetailView):
    """Отображает подробную информацию о выбранном товаре."""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class ProductCreateView(CreateView):
    """Создаёт новый товар через форму."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def form_valid(self, form):
        """Назначает новому товару категорию по умолчанию."""
        category, _ = Category.objects.get_or_create(
            name="Без категории",
            defaults={
                "description": "Товары, добавленные через форму.",
            },
        )
        form.instance.category = category
        return super().form_valid(form)

    def get_success_url(self):
        """Перенаправляет на страницу созданного товара."""
        return reverse(
            "catalog:product_detail",
            kwargs={"pk": self.object.pk},
        )


class ProductUpdateView(UpdateView):
    """Редактирует существующий товар."""

    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self):
        """Перенаправляет на страницу изменённого товара."""
        return reverse(
            "catalog:product_detail",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(DeleteView):
    """Удаляет товар после подтверждения."""

    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("catalog:home")


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
