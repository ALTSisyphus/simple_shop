from django.conf import settings
from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mailing_recipients")

    def __str__(self):
        return self.email


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mailing_messages")

    def __str__(self):
        return self.subject


class Mailing(models.Model):
    STATUS_CREATED = "Создана"
    STATUS_RUNNING = "Запущена"
    STATUS_FINISHED = "Завершена"
    STATUS_CHOICES = [(x, x) for x in (STATUS_CREATED, STATUS_RUNNING, STATUS_FINISHED)]

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="mailings")
    recipients = models.ManyToManyField(Recipient, related_name="mailings")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mailings")
    is_active = models.BooleanField(default=True)

    def update_status(self):
        now = timezone.now()
        if now < self.start_time:
            value = self.STATUS_CREATED
        elif self.start_time <= now <= self.end_time:
            value = self.STATUS_RUNNING
        else:
            value = self.STATUS_FINISHED
        if self.status != value:
            self.status = value
            self.save(update_fields=["status"])
        return value


class MailingAttempt(models.Model):
    STATUS_SUCCESS = "Успешно"
    STATUS_FAILED = "Не успешно"
    STATUS_CHOICES = [(STATUS_SUCCESS, STATUS_SUCCESS), (STATUS_FAILED, STATUS_FAILED)]

    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True)
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name="attempts")
