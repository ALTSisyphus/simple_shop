from django.contrib.auth import views as auth_views
from django.urls import path

from users.views import (
    ProfileUpdateView,
    RegisterView,
    UserLoginView,
    verify_email,
)

app_name = "users"

urlpatterns = [
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),
    path(
        "login/",
        UserLoginView.as_view(),
        name="login",
    ),
    path(
        "profile/",
        ProfileUpdateView.as_view(),
        name="profile",
    ),
    path(
        "verify/<str:token>/",
        verify_email,
        name="verify_email",
    ),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
