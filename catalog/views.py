from django.shortcuts import get_object_or_404, render

from catalog.models import Contact, Product


def home(request):
    """Отображает главную страницу каталога."""
    latest_products = Product.objects.order_by("-created_at")[:5]

    return render(
        request,
        "catalog/home.html",
        {"latest_products": latest_products},
    )


def product_detail(request, pk):
    """Отображает подробную информацию о выбранном товаре."""
    product = get_object_or_404(Product, pk=pk)

    return render(
        request,
        "catalog/product_detail.html",
        {"product": product},
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
