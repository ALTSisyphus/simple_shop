from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from users.models import User
from mailing.models import Mailing, Recipient
from users.views import ManagerRequiredMixin


class ManagerMailingListView(ManagerRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/manager_mailing_list.html"


class ManagerRecipientListView(ManagerRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing/manager_recipient_list.html"


class ManagerUserListView(ManagerRequiredMixin, ListView):
    model = User
    template_name = "mailing/manager_user_list.html"


def block_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_blocked = True
    user.save(update_fields=["is_blocked"])
    return redirect("mailing:manager_users")


def disable_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.is_active = False
    mailing.save(update_fields=["is_active"])
    return redirect("mailing:manager_mailings")
