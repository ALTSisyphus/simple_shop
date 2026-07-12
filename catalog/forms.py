from django import forms

from catalog.models import Product


class ProductForm(forms.ModelForm):
    """Форма добавления нового товара."""

    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "price",
            "image",
        )
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите название товара",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Введите описание товара",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "0.01",
                    "step": "0.01",
                    "placeholder": "0.00",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
        }
        labels = {
            "name": "Название",
            "description": "Описание",
            "price": "Цена",
            "image": "Изображение",
        }

    def __init__(self, *args, **kwargs):
        """Делает все отображаемые поля обязательными."""
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = True

    def clean_price(self):
        """Проверяет, что цена товара больше нуля."""
        price = self.cleaned_data["price"]

        if price <= 0:
            raise forms.ValidationError(
                "Цена должна быть больше нуля."
            )

        return price
