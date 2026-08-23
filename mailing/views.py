from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DetailView, ListView
from django.urls import reverse_lazy

from mailing.forms import MailingForm, MessageForm, RecipientForm
from mailing.models import Mailing, Message, Recipient
from mailing.services import send_mailing


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("mailing:list")
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailing:list")
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing:list")
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


def run_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    send_mailing(mailing)
    return redirect("mailing:detail", pk=pk)


@cache_page(60 * 15)
def statistics(request):
    key = f"mailing_stats_{request.user.pk}"
    result = cache.get(key)
    if result is None:
        mailings = Mailing.objects.filter(owner=request.user)
        result = {
            "mailings": mailings.count(),
            "active_mailings": mailings.filter(is_active=True, status=Mailing.STATUS_RUNNING).count(),
            "recipients": Recipient.objects.filter(owner=request.user).count(),
            "successful": sum(m.attempts.filter(status="Успешно").count() for m in mailings),
            "failed": sum(m.attempts.filter(status="Не успешно").count() for m in mailings),
        }
        cache.set(key, result, 900)
    return JsonResponse(result)
