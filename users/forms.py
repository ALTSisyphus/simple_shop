from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from users.models import User


class BootstrapFormMixin:
    """Добавляет полям формы Bootstrap-классы."""

    def apply_bootstrap(self):
        for field in self.fields.values():
            current = field.widget.attrs.get("class", "")
            css_class = (
                "form-check-input"
                if isinstance(field.widget, forms.CheckboxInput)
                else "form-control"
            )
            field.widget.attrs["class"] = f"{current} {css_class}".strip()


class UserRegistrationForm(BootstrapFormMixin, UserCreationForm):
    email = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(
            attrs={"autocomplete": "email", "autofocus": True}
        ),
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Пользователь с такой электронной почтой уже существует."
            )
        return email


class UserLoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(
            attrs={"autocomplete": "email", "autofocus": True}
        ),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

    def clean(self):
        email = self.cleaned_data.get("username")
        if email:
            self.cleaned_data["username"] = email.strip().lower()
        return super().clean()


class UserProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "avatar", "phone_number", "country")
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone_number": forms.TextInput(attrs={"autocomplete": "tel"}),
            "country": forms.TextInput(attrs={"autocomplete": "country-name"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        duplicate = User.objects.filter(email__iexact=email).exclude(
            pk=self.instance.pk
        )
        if duplicate.exists():
            raise forms.ValidationError(
                "Пользователь с такой электронной почтой уже существует."
            )
        return email
