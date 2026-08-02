import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from blog.forms import BlogForm
from catalog.forms import MAX_IMAGE_SIZE, ProductForm
from catalog.models import Category, Product


def create_test_image(
    image_format="PNG",
    filename=None,
    content_type=None,
    size=(10, 10),
    compress_level=None,
):
    """Создаёт настоящий файл изображения через Pillow."""
    output = io.BytesIO()
    image = Image.new("RGB", size, color="white")
    save_kwargs = {}

    if compress_level is not None and image_format == "PNG":
        save_kwargs["compress_level"] = compress_level

    image.save(output, format=image_format, **save_kwargs)

    extension = "jpg" if image_format == "JPEG" else image_format.lower()
    filename = filename or f"product.{extension}"
    content_type = content_type or (
        "image/jpeg" if image_format == "JPEG" else f"image/{extension}"
    )

    return SimpleUploadedFile(
        filename,
        output.getvalue(),
        content_type=content_type,
    )


class CatalogTestCase(TestCase):
    """Общая настройка тестов каталога."""

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
        shutil.rmtree(cls.media_root, ignore_errors=True)
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
        self.user = get_user_model().objects.create_user(
            email="catalog-tests@example.com",
            password="StrongPass123!",
        )
        self.client.force_login(self.user)

    @staticmethod
    def valid_form_data(**overrides):
        data = {
            "name": "Новый товар",
            "description": "Описание нового товара.",
            "price": "250.50",
        }
        data.update(overrides)
        return data


class CatalogViewsTests(CatalogTestCase):
    """Тесты полного CRUD товаров."""

    def test_product_list_opens_and_displays_detail_link(self):
        response = self.client.get(reverse("catalog:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/home.html")
        self.assertContains(response, self.product.name)
        self.assertContains(
            response,
            reverse(
                "catalog:product_detail",
                kwargs={"pk": self.product.pk},
            ),
        )

    def test_product_detail_opens_and_displays_actions(self):
        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={"pk": self.product.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/product_detail.html")
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)
        self.assertContains(response, "100,00")
        self.assertContains(response, "Редактировать")
        self.assertContains(response, "Удалить")
        self.assertContains(response, "Назад на главную")

    def test_unknown_product_returns_404(self):
        routes = (
            "catalog:product_detail",
            "catalog:product_update",
            "catalog:product_delete",
        )

        for route_name in routes:
            with self.subTest(route_name=route_name):
                response = self.client.get(
                    reverse(route_name, kwargs={"pk": 999999})
                )
                self.assertEqual(response.status_code, 404)

    def test_home_paginates_six_products(self):
        for number in range(6):
            Product.objects.create(
                name=f"Товар {number}",
                description="Описание товара.",
                category=self.category,
                price="10.00",
            )

        first_page = self.client.get(reverse("catalog:home"))
        second_page = self.client.get(
            reverse("catalog:home"),
            {"page": 2},
        )

        self.assertEqual(len(first_page.context["products"]), 6)
        self.assertEqual(len(second_page.context["products"]), 1)
        self.assertContains(first_page, "Вперёд")
        self.assertContains(second_page, "Назад")

    def test_valid_product_is_created_and_redirects_to_detail(self):
        response = self.client.post(
            reverse("catalog:product_create"),
            data={
                **self.valid_form_data(),
                "image": create_test_image("PNG"),
            },
        )

        product = Product.objects.get(name="Новый товар")
        self.assertRedirects(
            response,
            reverse(
                "catalog:product_detail",
                kwargs={"pk": product.pk},
            ),
        )
        self.assertEqual(product.category.name, "Без категории")
        self.assertTrue(product.image.name.startswith("products/"))

    def test_product_is_updated_and_category_is_preserved(self):
        response = self.client.post(
            reverse(
                "catalog:product_update",
                kwargs={"pk": self.product.pk},
            ),
            data={
                **self.valid_form_data(
                    name="Изменённый товар",
                    description="Новое описание.",
                    price="0",
                ),
                "image": create_test_image("JPEG"),
            },
        )

        self.product.refresh_from_db()
        self.assertRedirects(
            response,
            reverse(
                "catalog:product_detail",
                kwargs={"pk": self.product.pk},
            ),
        )
        self.assertEqual(self.product.name, "Изменённый товар")
        self.assertEqual(self.product.description, "Новое описание.")
        self.assertEqual(str(self.product.price), "0.00")
        self.assertEqual(self.product.category, self.category)

    def test_product_delete_get_only_shows_confirmation(self):
        response = self.client.get(
            reverse(
                "catalog:product_delete",
                kwargs={"pk": self.product.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "catalog/product_confirm_delete.html",
        )
        self.assertContains(response, self.product.name)
        self.assertTrue(
            Product.objects.filter(pk=self.product.pk).exists()
        )

    def test_product_is_deleted_by_post(self):
        response = self.client.post(
            reverse(
                "catalog:product_delete",
                kwargs={"pk": self.product.pk},
            )
        )

        self.assertRedirects(response, reverse("catalog:home"))
        self.assertFalse(
            Product.objects.filter(pk=self.product.pk).exists()
        )


class ProductFormValidationTests(CatalogTestCase):
    """Тесты серверной валидации формы товара."""

    def build_form(self, data=None, image=None, instance=None):
        return ProductForm(
            data=data or self.valid_form_data(),
            files={"image": image or create_test_image("PNG")},
            instance=instance,
        )

    def test_all_product_form_fields_are_required(self):
        form = ProductForm()

        for field_name in ("name", "description", "price", "image"):
            with self.subTest(field_name=field_name):
                self.assertTrue(form.fields[field_name].required)

    def test_empty_product_form_shows_required_errors(self):
        response = self.client.post(
            reverse("catalog:product_create"),
            {},
        )
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        for field_name in ("name", "description", "price", "image"):
            with self.subTest(field_name=field_name):
                self.assertFormError(
                    form,
                    field_name,
                    "Обязательное поле.",
                )

    def test_forbidden_words_are_rejected_in_name(self):
        values = (
            "БЕСПЛАТНО получите товар",
            "Лучшее КаЗиНо",
            "Устройство РАДАР",
        )

        for value in values:
            with self.subTest(value=value):
                form = self.build_form(
                    data=self.valid_form_data(name=value)
                )
                self.assertFalse(form.is_valid())
                self.assertIn("запрещённое слово", form.errors["name"][0])

    def test_forbidden_words_are_rejected_in_description(self):
        values = (
            "Новости про криптовалюту",
            "Это ОБМАН покупателя",
            "Новая БиРжА для клиентов",
        )

        for value in values:
            with self.subTest(value=value):
                form = self.build_form(
                    data=self.valid_form_data(description=value)
                )
                self.assertFalse(form.is_valid())
                self.assertIn(
                    "запрещённое слово",
                    form.errors["description"][0],
                )

    def test_text_without_forbidden_words_is_valid(self):
        form = self.build_form(
            data=self.valid_form_data(
                name="Полезный учебный товар",
                description="Подробное и честное описание товара.",
            )
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_negative_price_is_rejected_with_clear_error(self):
        form = self.build_form(
            data=self.valid_form_data(price="-1")
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["price"],
            ["Цена не может быть отрицательной."],
        )

    def test_zero_and_positive_prices_are_accepted(self):
        for price in ("0", "1.00", "250.50"):
            with self.subTest(price=price):
                form = self.build_form(
                    data=self.valid_form_data(price=price)
                )
                self.assertTrue(form.is_valid(), form.errors)

    def test_product_form_uses_bootstrap_classes_and_attributes(self):
        form = ProductForm()

        for field_name in ("name", "description", "price", "image"):
            with self.subTest(field_name=field_name):
                classes = form.fields[field_name].widget.attrs[
                    "class"
                ].split()
                self.assertEqual(classes.count("form-control"), 1)

        self.assertEqual(
            form.fields["price"].widget.attrs["min"],
            "0",
        )
        self.assertEqual(
            form.fields["price"].widget.attrs["step"],
            "0.01",
        )
        self.assertEqual(
            form.fields["image"].widget.attrs["accept"],
            "image/jpeg,image/png",
        )

    def test_blog_checkbox_keeps_bootstrap_styling(self):
        blog_form = BlogForm()
        classes = blog_form.fields["is_published"].widget.attrs[
            "class"
        ].split()

        self.assertIn("form-check-input", classes)

        response = self.client.get(reverse("blog:blog_create"))
        self.assertContains(response, 'class="form-check mb-3"')


class ProductImageValidationTests(CatalogTestCase):
    """Тесты фактического формата и размера изображений."""

    def build_form(self, image, instance=None):
        return ProductForm(
            data=self.valid_form_data(),
            files={"image": image} if image is not None else {},
            instance=instance,
        )

    def test_png_and_jpeg_images_are_accepted(self):
        cases = (
            ("PNG", "image/png"),
            ("JPEG", "image/jpeg"),
        )

        for image_format, content_type in cases:
            with self.subTest(image_format=image_format):
                form = self.build_form(
                    create_test_image(
                        image_format,
                        content_type=content_type,
                    )
                )
                self.assertTrue(form.is_valid(), form.errors)

    def test_gif_image_is_rejected(self):
        form = self.build_form(
            create_test_image(
                "GIF",
                content_type="image/gif",
            )
        )

        self.assertFalse(form.is_valid())
        self.assertIn("JPEG и PNG", form.errors["image"][0])

    def test_image_larger_than_five_megabytes_is_rejected(self):
        oversized_image = create_test_image(
            "PNG",
            size=(1500, 1500),
            compress_level=0,
        )
        self.assertGreater(oversized_image.size, MAX_IMAGE_SIZE)

        form = self.build_form(oversized_image)

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["image"],
            ["Размер изображения не должен превышать 5 МБ."],
        )

    def test_existing_image_can_be_kept_during_update(self):
        self.product.image.save(
            "existing.png",
            create_test_image("PNG"),
            save=True,
        )

        response = self.client.post(
            reverse(
                "catalog:product_update",
                kwargs={"pk": self.product.pk},
            ),
            data=self.valid_form_data(
                name="Товар с прежним изображением"
            ),
        )

        self.product.refresh_from_db()
        self.assertRedirects(
            response,
            reverse(
                "catalog:product_detail",
                kwargs={"pk": self.product.pk},
            ),
        )
        self.assertTrue(self.product.image.name.endswith("existing.png"))
