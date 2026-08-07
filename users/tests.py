from django.contrib.auth import authenticate, get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product

User = get_user_model()


class UsersTests(TestCase):
    def test_user_is_created_and_authenticated_by_email(self):
        user = User.objects.create_user(
            email="student@example.com",
            password="StrongPass123!",
        )

        authenticated = authenticate(
            username="student@example.com",
            password="StrongPass123!",
        )

        self.assertEqual(authenticated, user)
        self.assertIsNone(user.username)

    def test_registration_creates_user_and_sends_email(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "email": "new@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["new@example.com"])

    def test_product_pages_require_authentication(self):
        category = Category.objects.create(name="Категория")
        product = Product.objects.create(
            name="Товар",
            description="Описание",
            category=category,
            price="100.00",
        )

        protected_urls = (
            reverse("catalog:product_create"),
            reverse("catalog:product_detail", kwargs={"pk": product.pk}),
            reverse("catalog:product_update", kwargs={"pk": product.pk}),
            reverse("catalog:product_delete", kwargs={"pk": product.pk}),
        )

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f"{reverse('users:login')}?next={url}",
                )

        self.assertEqual(self.client.get(reverse("catalog:home")).status_code, 200)
