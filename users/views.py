from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth import views as auth_views
from django.utils.crypto import get_random_string
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
        user = form.save(commit=False)
        user.email_verification_token = get_random_string(48)
        user.email_verified = False
        user.save()

        self.object = user

        response = super().form_valid(form)

        try:
            send_mail(
                subject="Подтверждение email Skystore",
                message=(
                    "Для подтверждения email перейдите по ссылке:\\n"
                    f"{self.request.build_absolute_uri('/users/verify/')}"
                    f"{user.email_verification_token}/"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except (SMTPException, OSError):
            messages.warning(
                self.request,
                "Аккаунт создан, но письмо подтверждения отправить не удалось.",
            )
        else:
            messages.success(
                self.request,
                "Регистрация завершена. Проверьте email для подтверждения.",
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


def verify_email(request, token):
    user = get_object_or_404(User, email_verification_token=token)
    user.email_verified = True
    user.email_verification_token = ""
    user.save(update_fields=["email_verified", "email_verification_token"])
    return redirect("users:login")


class ManagerRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != User.ROLE_MANAGER:
            return HttpResponseForbidden("Недостаточно прав")
        return super().dispatch(request, *args, **kwargs)
