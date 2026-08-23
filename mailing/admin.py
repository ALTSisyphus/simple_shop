from django.contrib import admin
from mailing.models import Mailing, MailingAttempt, Message, Recipient

admin.site.register([Mailing, MailingAttempt, Message, Recipient])
