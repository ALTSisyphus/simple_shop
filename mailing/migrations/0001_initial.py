from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("users", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Recipient",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("full_name", models.CharField(max_length=255)),
                ("comment", models.TextField(blank=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mailing_recipients", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mailing_messages", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Mailing",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("status", models.CharField(choices=[("Создана", "Создана"), ("Запущена", "Запущена"), ("Завершена", "Завершена")], default="Создана", max_length=20)),
                ("message", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mailings", to="mailing.message")),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="mailings", to=settings.AUTH_USER_MODEL)),
                ("recipients", models.ManyToManyField(related_name="mailings", to="mailing.recipient")),
            ],
        ),
        migrations.CreateModel(
            name="MailingAttempt",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("attempt_time", models.DateTimeField(auto_now_add=True)),
                ("status", models.CharField(choices=[("Успешно", "Успешно"), ("Не успешно", "Не успешно")], max_length=20)),
                ("server_response", models.TextField(blank=True)),
                ("mailing", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="mailing.mailing")),
            ],
        ),
    ]
