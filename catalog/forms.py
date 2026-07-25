from django import forms
from django.core.files.uploadedfile import UploadedFile
from PIL import Image as PillowImage
from PIL import UnidentifiedImageError

from catalog.models import Product

FORBIDDEN_WORDS = (
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
)

MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG"}
ALLOWED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png"}


class ProductForm(forms.ModelForm):
    """Форма создания и редактирования товара."""

    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "price",
            "image",
        )
        widgets = {
            "name": forms.TextInput(),
            "description": forms.Textarea(),
            "price": forms.NumberInput(),
            "image": forms.ClearableFileInput(),
        }
        labels = {
            "name": "Название",
            "description": "Описание",
            "price": "Цена",
            "image": "Изображение",
        }

    def __init__(self, *args, **kwargs):
        """Настраивает обязательность, Bootstrap-классы и атрибуты полей."""
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = True
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                bootstrap_class = "form-check-input"
            elif isinstance(widget, forms.Select):
                bootstrap_class = "form-select"
            else:
                bootstrap_class = "form-control"

            current_classes = widget.attrs.get("class", "").split()
            if bootstrap_class not in current_classes:
                current_classes.append(bootstrap_class)
            widget.attrs["class"] = " ".join(current_classes)

        self.fields["name"].widget.attrs["placeholder"] = (
            "Введите название товара"
        )
        self.fields["description"].widget.attrs.update(
            {
                "placeholder": "Введите описание товара",
                "rows": 5,
            }
        )
        self.fields["price"].widget.attrs.update(
            {
                "min": "0",
                "step": "0.01",
                "placeholder": "0.00",
            }
        )
        self.fields["image"].widget.attrs["accept"] = (
            "image/jpeg,image/png"
        )

    @staticmethod
    def _validate_forbidden_words(value):
        """Проверяет текст на запрещённые слова без учёта регистра."""
        normalized_value = value.casefold()

        for forbidden_word in FORBIDDEN_WORDS:
            normalized_word = forbidden_word.casefold()
            search_variants = {normalized_word}

            if normalized_word.endswith(("а", "я")):
                search_variants.add(normalized_word[:-1])

            if any(
                variant in normalized_value
                for variant in search_variants
            ):
                raise forms.ValidationError(
                    "Поле содержит запрещённое слово: "
                    f"«{forbidden_word}»."
                )

        return value

    def clean_name(self):
        """Проверяет название товара на запрещённые слова."""
        return self._validate_forbidden_words(
            self.cleaned_data["name"]
        )

    def clean_description(self):
        """Проверяет описание товара на запрещённые слова."""
        return self._validate_forbidden_words(
            self.cleaned_data["description"]
        )

    def clean_price(self):
        """Запрещает отрицательную цену, разрешая нулевую."""
        price = self.cleaned_data["price"]

        if price < 0:
            raise forms.ValidationError(
                "Цена не может быть отрицательной."
            )

        return price

    def clean_image(self):
        """Проверяет размер, MIME-тип и фактический формат нового файла."""
        image = self.cleaned_data.get("image")

        if not image or not isinstance(image, UploadedFile):
            return image

        if image.size > MAX_IMAGE_SIZE:
            raise forms.ValidationError(
                "Размер изображения не должен превышать 5 МБ."
            )

        if image.content_type not in ALLOWED_IMAGE_MIME_TYPES:
            raise forms.ValidationError(
                "Допустимы только изображения JPEG и PNG."
            )

        current_position = image.tell()

        try:
            image.seek(0)
            with PillowImage.open(image) as pillow_image:
                actual_format = pillow_image.format
                pillow_image.verify()
        except (UnidentifiedImageError, OSError, SyntaxError, ValueError):
            raise forms.ValidationError(
                "Загруженный файл не является корректным изображением."
            )
        finally:
            image.seek(current_position)

        if actual_format not in ALLOWED_IMAGE_FORMATS:
            raise forms.ValidationError(
                "Допустимы только изображения JPEG и PNG."
            )

        return image
