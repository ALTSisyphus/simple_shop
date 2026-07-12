from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from catalog.forms import ProductForm
from catalog.models import Category, Contact, Product


def home(request):
    """Отображает главную страницу с постраничным списком товаров."""
    products = Product.objects.all()

    paginator = Paginator(products, 6)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "products": page_obj,
        "page_obj": page_obj,
    }

    return render(
        request,
        "catalog/home.html",
        context,
    )


def product_detail(request, pk):
    """Отображает подробную информацию о выбранном товаре."""
    product = get_object_or_404(Product, pk=pk)

    return render(
        request,
        "catalog/product_detail.html",
        {"product": product},
    )


def product_create(request):
    """Создаёт новый товар через форму."""
    if request.method == "POST":
        form = ProductForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            product = form.save(commit=False)

            category, _ = Category.objects.get_or_create(
                name="Без категории",
                defaults={
                    "description": (
                        "Товары, добавленные через форму."
                    ),
                },
            )

            product.category = category
            product.save()

            return redirect("catalog:home")
    else:
        form = ProductForm()

    return render(
        request,
        "catalog/product_form.html",
        {"form": form},
    )


def contacts(request):
    """Отображает контакты и обрабатывает форму обратной связи."""
    success_message = None

    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        message = request.POST.get("message")

        print("Получено сообщение обратной связи:")
        print(f"Имя: {name}")
        print(f"Телефон: {phone}")
        print(f"Сообщение: {message}")

        success_message = "Сообщение успешно отправлено!"

    context = {
        "success_message": success_message,
        "contacts": Contact.objects.all(),
    }

    return render(
        request,
        "catalog/contacts.html",
        context,
    )
