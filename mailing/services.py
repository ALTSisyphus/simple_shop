from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from mailing.models import MailingAttempt


def send_mailing(mailing):
    now = timezone.now()
    if not (mailing.start_time <= now <= mailing.end_time):
        raise ValueError("Отправка рассылки недоступна в текущее время")

    attempts = []
    for recipient in mailing.recipients.all():
        try:
            send_mail(
                mailing.message.subject,
                mailing.message.body,
                None,
                [recipient.email],
                fail_silently=False,
            )
        except Exception as exc:
            attempts.append(MailingAttempt(
                mailing=mailing,
                status=MailingAttempt.STATUS_FAILED,
                server_response=str(exc),
            ))
        else:
            attempts.append(MailingAttempt(
                mailing=mailing,
                status=MailingAttempt.STATUS_SUCCESS,
                server_response="OK",
            ))
    with transaction.atomic():
        MailingAttempt.objects.bulk_create(attempts)
    return attempts
