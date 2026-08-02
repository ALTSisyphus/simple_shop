from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import UserManager


class User(AbstractUser):
    """Пользователь с авторизацией по электронной почте."""

    username = None
    email = models.EmailField(
        unique=True,
        verbose_name="электронная почта",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="аватар",
    )
    phone_number = models.CharField(
        max_length=35,
        blank=True,
        verbose_name="номер телефона",
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="страна",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.email
