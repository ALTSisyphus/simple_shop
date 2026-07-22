from django import forms

from blog.models import Blog


class BlogForm(forms.ModelForm):
    """Форма создания и редактирования блоговой записи."""

    class Meta:
        model = Blog
        fields = (
            "title",
            "content",
            "preview",
            "is_published",
        )
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок статьи",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 8,
                    "placeholder": "Введите содержимое статьи",
                }
            ),
            "preview": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "is_published": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
