from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=150, verbose_name="название")
    description = models.TextField(blank=True, verbose_name="описание")

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="наименование")
    description = models.TextField(blank=True, verbose_name="описание")
    image = models.ImageField(
        upload_to="products/", blank=True, null=True, verbose_name="изображение"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="категория",
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="цена за покупку"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="дата изменения")

    class Meta:
        verbose_name = "продукт"
        verbose_name_plural = "продукты"

    def __str__(self):
        return self.name


class Contact(models.Model):
    country = models.CharField(max_length=100, verbose_name="страна")
    tax_id = models.CharField(max_length=50, verbose_name="ИНН")
    address = models.TextField(verbose_name="адрес")

    class Meta:
        verbose_name = "контактные данные"
        verbose_name_plural = "контактные данные"

    def __str__(self):
        return f"{self.country}: {self.address}"
