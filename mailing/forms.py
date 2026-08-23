from django import forms
from django.utils import timezone

from mailing.models import Mailing, Message, Recipient


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        exclude = ("owner",)


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude = ("owner",)


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        exclude = ("owner", "status")

    def clean(self):
        data = super().clean()
        if data.get("start_time") and data["start_time"] < timezone.now():
            raise forms.ValidationError("Дата начала не может быть в прошлом")
        if data.get("start_time") and data.get("end_time") and data["start_time"] >= data["end_time"]:
            raise forms.ValidationError("Дата начала должна быть раньше окончания")
        return data
