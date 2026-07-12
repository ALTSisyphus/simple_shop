import base64
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from catalog.forms import ProductForm
from catalog.models import Category, Product


TEST_IMAGE = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
)


class CatalogViewsTests(TestCase):
    """Тесты страниц каталога и формы создания товара."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.media_root = tempfile.mkdtemp()
        cls.media_override = override_settings(
            MEDIA_ROOT=cls.media_root
        )
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls.media_override.disable()
        shutil.rmtree(
            cls.media_root,
            ignore_errors=True,
        )

        super().tearDownClass()

    def setUp(self):
        self.category = Category.objects.create(
            name="Тестовая категория",
            description="Категория для автоматических тестов.",
        )

        self.product = Product.objects.create(
            name="Тестовый товар",
            description="Подробное описание тестового товара.",
            category=self.category,
            price="100.00",
        )

    def test_home_displays_products_and_detail_link(self):
        """Главная страница выводит товар и ссылку на детали."""
        response = self.client.get(
            reverse("catalog:home")
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "catalog/home.html",
        )
        self.assertTemplateUsed(
            response,
            "catalog/base.html",
        )
        self.assertContains(
            response,
            self.product.name,
        )
        self.assertContains(
            response,
            reverse(
                "catalog:product_detail",
                kwargs={"pk": self.product.pk},
            ),
        )

    def test_product_detail_displays_all_product_data(self):
        """Детальная страница выводит все данные товара."""
        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={"pk": self.product.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "catalog/product_detail.html",
        )
        self.assertTemplateUsed(
            response,
            "catalog/base.html",
        )
        self.assertContains(
            response,
            self.product.name,
        )
        self.assertContains(
            response,
            self.product.description,
        )
        self.assertContains(
            response,
            "100,00",
        )
        self.assertContains(
            response,
            "Назад на главную",
        )

    def test_product_detail_returns_404_for_unknown_product(self):
        """Несуществующий товар возвращает ответ 404."""
        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={"pk": 999999},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_home_paginates_six_products(self):
        """Главная страница выводит по шесть товаров."""
        for number in range(6):
            Product.objects.create(
                name=f"Товар {number}",
                description="Описание товара.",
                category=self.category,
                price="10.00",
            )

        first_page = self.client.get(
            reverse("catalog:home")
        )
        second_page = self.client.get(
            reverse("catalog:home"),
            {"page": 2},
        )

        self.assertEqual(
            len(first_page.context["products"]),
            6,
        )
        self.assertEqual(
            len(second_page.context["products"]),
            1,
        )
        self.assertContains(
            first_page,
            "Вперёд",
        )
        self.assertContains(
            second_page,
            "Назад",
        )

    def test_product_form_fields_are_required(self):
        """Все поля формы товара являются обязательными."""
        form = ProductForm()

        required_fields = (
            "name",
            "description",
            "price",
            "image",
        )

        for field_name in required_fields:
            self.assertTrue(
                form.fields[field_name].required
            )

    def test_product_create_shows_errors_for_empty_form(self):
        """Пустая форма показывает ошибки обязательных полей."""
        response = self.client.post(
            reverse("catalog:product_create"),
            {},
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        form = response.context["form"]

        self.assertFormError(
            form,
            "name",
            "Обязательное поле.",
        )
        self.assertFormError(
            form,
            "description",
            "Обязательное поле.",
        )
        self.assertFormError(
            form,
            "price",
            "Обязательное поле.",
        )
        self.assertFormError(
            form,
            "image",
            "Обязательное поле.",
        )

    def test_product_create_rejects_non_positive_price(self):
        """Форма не принимает нулевую цену."""
        image = SimpleUploadedFile(
            "product.gif",
            TEST_IMAGE,
            content_type="image/gif",
        )

        response = self.client.post(
            reverse("catalog:product_create"),
            {
                "name": "Товар с неверной ценой",
                "description": "Описание товара.",
                "price": "0",
                "image": image,
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertFormError(
            response.context["form"],
            "price",
            "Цена должна быть больше нуля.",
        )
        self.assertFalse(
            Product.objects.filter(
                name="Товар с неверной ценой"
            ).exists()
        )

    def test_product_create_saves_product_and_redirects(self):
        """Валидная форма сохраняет товар и перенаправляет."""
        image = SimpleUploadedFile(
            "product.gif",
            TEST_IMAGE,
            content_type="image/gif",
        )

        response = self.client.post(
            reverse("catalog:product_create"),
            {
                "name": "Новый товар",
                "description": "Описание нового товара.",
                "price": "250.50",
                "image": image,
            },
        )

        self.assertRedirects(
            response,
            reverse("catalog:home"),
        )

        product = Product.objects.get(
            name="Новый товар"
        )

        self.assertEqual(
            product.category.name,
            "Без категории",
        )
        self.assertTrue(
            product.image.name.startswith("products/")
        )
