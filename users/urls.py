from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.views import verify_email, ProfileUpdateView, RegisterView, UserLoginView

app_name = UsersConfig.name

urlpatterns = [
    path(
        "verify/<str:token>/",
        verify_email,
        name="verify_email",
    ),

    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path(
        "logout/",
        LogoutView.as_view(next_page=reverse_lazy("catalog:home")),
        name="logout",
    ),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
]

# email verification route
