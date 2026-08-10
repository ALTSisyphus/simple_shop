from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from users.forms import (
    UserLoginForm,
    UserProfileForm,
    UserRegistrationForm,
)
from users.models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)

        try:
            send_mail(
                subject="Добро пожаловать в Skystore",
                message=(
                    "Регистрация завершена. Теперь вы можете войти "
                    "в Skystore по электронной почте и паролю."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.object.email],
                fail_silently=False,
            )
        except (SMTPException, OSError):
            messages.warning(
                self.request,
                "Аккаунт создан, но приветственное письмо отправить не удалось.",
            )
        else:
            messages.success(
                self.request,
                "Регистрация завершена. Приветственное письмо отправлено.",
            )

        return response


class UserLoginView(LoginView):
    template_name = "users/login.html"
    authentication_form = UserLoginForm
    redirect_authenticated_user = True


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Профиль сохранён.")
        return super().form_valid(form)
