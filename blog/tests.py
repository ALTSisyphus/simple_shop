import base64
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from blog.models import Blog


TEST_IMAGE = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
)


class BlogModelTests(TestCase):
    """Тесты модели блоговой записи."""

    def test_string_representation_returns_title(self):
        """Метод __str__ возвращает заголовок статьи."""
        blog = Blog.objects.create(
            title="Тестовая статья",
            content="Содержимое тестовой статьи.",
        )

        self.assertEqual(
            str(blog),
            "Тестовая статья",
        )


class BlogViewsTests(TestCase):
    """Тесты страниц и CRUD блоговых записей."""

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
        self.content_manager = get_user_model().objects.create_user(
            email="content-manager@example.com",
            password="StrongPass123!",
        )
        permissions = Permission.objects.filter(
            content_type__app_label="blog",
            codename__in=("add_blog", "change_blog", "delete_blog"),
        )
        self.content_manager.user_permissions.set(permissions)
        self.client.force_login(self.content_manager)

        self.published_blog = Blog.objects.create(
            title="Опубликованная статья",
            content="Содержимое опубликованной статьи.",
            is_published=True,
        )
        self.unpublished_blog = Blog.objects.create(
            title="Черновик статьи",
            content="Содержимое неопубликованной статьи.",
            is_published=False,
        )

    def test_blog_list_opens(self):
        """Страница списка статей открывается."""
        response = self.client.get(
            reverse("blog:blog_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "blog/blog_list.html",
        )
        self.assertTemplateUsed(
            response,
            "catalog/base.html",
        )

    def test_blog_list_displays_published_blog(self):
        """В списке отображается опубликованная статья."""
        response = self.client.get(
            reverse("blog:blog_list")
        )

        self.assertContains(
            response,
            self.published_blog.title,
        )
        self.assertContains(
            response,
            reverse(
                "blog:blog_detail",
                kwargs={"pk": self.published_blog.pk},
            ),
        )

    def test_blog_list_hides_unpublished_blog(self):
        """В списке не отображается неопубликованная статья."""
        response = self.client.get(
            reverse("blog:blog_list")
        )

        self.assertNotContains(
            response,
            self.unpublished_blog.title,
        )

    def test_blog_detail_opens(self):
        """Детальная страница статьи открывается."""
        response = self.client.get(
            reverse(
                "blog:blog_detail",
                kwargs={"pk": self.published_blog.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "blog/blog_detail.html",
        )
        self.assertTemplateUsed(
            response,
            "catalog/base.html",
        )
        self.assertContains(
            response,
            self.published_blog.title,
        )
        self.assertContains(
            response,
            self.published_blog.content,
        )

    def test_blog_detail_increases_views_count(self):
        """Открытие статьи увеличивает счётчик просмотров."""
        initial_views_count = self.published_blog.views_count

        self.client.get(
            reverse(
                "blog:blog_detail",
                kwargs={"pk": self.published_blog.pk},
            )
        )

        self.published_blog.refresh_from_db()

        self.assertEqual(
            self.published_blog.views_count,
            initial_views_count + 1,
        )

    def test_blog_create_page_opens(self):
        """Страница создания статьи открывается."""
        response = self.client.get(
            reverse("blog:blog_create")
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "blog/blog_form.html",
        )
        self.assertTemplateUsed(
            response,
            "catalog/base.html",
        )

    def test_blog_create_saves_blog_and_redirects_to_detail(self):
        """POST-запрос создаёт статью и перенаправляет на неё."""
        preview = SimpleUploadedFile(
            "blog-preview.gif",
            TEST_IMAGE,
            content_type="image/gif",
        )

        response = self.client.post(
            reverse("blog:blog_create"),
            {
                "title": "Новая статья",
                "content": "Содержимое новой статьи.",
                "preview": preview,
                "is_published": "on",
            },
        )

        blog = Blog.objects.get(
            title="Новая статья"
        )

        self.assertEqual(
            response.status_code,
            302,
        )
        self.assertEqual(
            response.url,
            reverse(
                "blog:blog_detail",
                kwargs={"pk": blog.pk},
            ),
        )
        self.assertEqual(
            blog.content,
            "Содержимое новой статьи.",
        )
        self.assertTrue(
            blog.is_published,
        )
        self.assertTrue(
            blog.preview.name.startswith("blog/")
        )

    def test_blog_update_page_opens(self):
        """Страница редактирования статьи открывается."""
        response = self.client.get(
            reverse(
                "blog:blog_update",
                kwargs={"pk": self.published_blog.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "blog/blog_form.html",
        )
        self.assertTemplateUsed(
            response,
            "catalog/base.html",
        )
        self.assertContains(
            response,
            self.published_blog.title,
        )

    def test_blog_update_changes_blog(self):
        """POST-запрос изменяет существующую статью."""
        response = self.client.post(
            reverse(
                "blog:blog_update",
                kwargs={"pk": self.published_blog.pk},
            ),
            {
                "title": "Изменённая статья",
                "content": "Обновлённое содержимое статьи.",
                "is_published": "on",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.published_blog.refresh_from_db()

        self.assertEqual(
            self.published_blog.title,
            "Изменённая статья",
        )
        self.assertEqual(
            self.published_blog.content,
            "Обновлённое содержимое статьи.",
        )
        self.assertTrue(
            self.published_blog.is_published,
        )

    def test_blog_update_redirects_to_updated_blog(self):
        """После редактирования открывается изменённая статья."""
        response = self.client.post(
            reverse(
                "blog:blog_update",
                kwargs={"pk": self.published_blog.pk},
            ),
            {
                "title": "Статья после редактирования",
                "content": "Новое содержимое.",
                "is_published": "on",
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "blog:blog_detail",
                kwargs={"pk": self.published_blog.pk},
            ),
            fetch_redirect_response=False,
        )

    def test_blog_delete_page_opens(self):
        """Страница подтверждения удаления открывается."""
        response = self.client.get(
            reverse(
                "blog:blog_delete",
                kwargs={"pk": self.published_blog.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertTemplateUsed(
            response,
            "blog/blog_confirm_delete.html",
        )
        self.assertTemplateUsed(
            response,
            "catalog/base.html",
        )
        self.assertContains(
            response,
            self.published_blog.title,
        )

    def test_blog_delete_removes_blog(self):
        """POST-запрос удаляет блоговую запись."""
        blog_pk = self.published_blog.pk

        response = self.client.post(
            reverse(
                "blog:blog_delete",
                kwargs={"pk": blog_pk},
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )
        self.assertFalse(
            Blog.objects.filter(pk=blog_pk).exists()
        )

    def test_blog_delete_redirects_to_list(self):
        """После удаления открывается список статей."""
        response = self.client.post(
            reverse(
                "blog:blog_delete",
                kwargs={"pk": self.published_blog.pk},
            )
        )

        self.assertRedirects(
            response,
            reverse("blog:blog_list"),
        )

    def test_unknown_blog_detail_returns_404(self):
        """Неизвестный идентификатор статьи возвращает 404."""
        response = self.client.get(
            reverse(
                "blog:blog_detail",
                kwargs={"pk": 999999},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_unknown_blog_update_returns_404(self):
        """Редактирование неизвестной статьи возвращает 404."""
        response = self.client.get(
            reverse(
                "blog:blog_update",
                kwargs={"pk": 999999},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_unknown_blog_delete_returns_404(self):
        """Удаление неизвестной статьи возвращает 404."""
        response = self.client.get(
            reverse(
                "blog:blog_delete",
                kwargs={"pk": 999999},
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )


class BlogPermissionsTests(TestCase):
    """Тесты доступа к изменению блога для дополнительного задания."""

    def setUp(self):
        self.blog = Blog.objects.create(
            title="Статья для проверки прав",
            content="Содержимое статьи.",
            is_published=True,
        )
        self.user = get_user_model().objects.create_user(
            email="ordinary-blog-user@example.com",
            password="StrongPass123!",
        )
        self.product_moderator = get_user_model().objects.create_user(
            email="product-moderator@example.com",
            password="StrongPass123!",
        )
        product_permissions = Permission.objects.filter(
            content_type__app_label="catalog",
            codename__in=(
                "can_unpublish_product",
                "change_product",
                "delete_product",
            ),
        )
        self.product_moderator.user_permissions.set(product_permissions)

    def test_ordinary_user_cannot_modify_blog(self):
        self.client.force_login(self.user)

        for route_name, kwargs in (
            ("blog:blog_create", {}),
            ("blog:blog_update", {"pk": self.blog.pk}),
            ("blog:blog_delete", {"pk": self.blog.pk}),
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name, kwargs=kwargs))
                self.assertEqual(response.status_code, 403)

    def test_product_moderator_cannot_modify_blog(self):
        self.client.force_login(self.product_moderator)

        for route_name, kwargs in (
            ("blog:blog_create", {}),
            ("blog:blog_update", {"pk": self.blog.pk}),
            ("blog:blog_delete", {"pk": self.blog.pk}),
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name, kwargs=kwargs))
                self.assertEqual(response.status_code, 403)
