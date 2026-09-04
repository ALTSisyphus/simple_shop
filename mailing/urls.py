from django.urls import path

from mailing import manager_views
from mailing.views import (
    MailingCreateView,
    MailingDetailView,
    MailingListView,
    MessageCreateView,
    RecipientCreateView,
    dashboard,
    run_mailing,
)

app_name = "mailing"

urlpatterns = [
    path("", MailingListView.as_view(), name="list"),
    path("dashboard/", dashboard, name="dashboard"),
    path("create/", MailingCreateView.as_view(), name="create"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path("recipient/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("<int:pk>/", MailingDetailView.as_view(), name="detail"),
    path("<int:pk>/run/", run_mailing, name="run"),
    path("manager/mailings/", manager_views.ManagerMailingListView.as_view(), name="manager_mailings"),
    path("manager/recipients/", manager_views.ManagerRecipientListView.as_view(), name="manager_recipients"),
    path("manager/users/", manager_views.ManagerUserListView.as_view(), name="manager_users"),
    path("manager/users/<int:pk>/block/", manager_views.block_user, name="block_user"),
    path("manager/mailings/<int:pk>/disable/", manager_views.disable_mailing, name="disable_mailing"),
]
