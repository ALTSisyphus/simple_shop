from django.urls import path
from mailing import views

app_name = "mailing"

urlpatterns = [
    path("", views.MailingListView.as_view(), name="list"),
    path("create/", views.MailingCreateView.as_view(), name="create"),
    path("<int:pk>/", views.MailingDetailView.as_view(), name="detail"),
    path("<int:pk>/send/", views.run_mailing, name="send"),
    path("statistics/", views.statistics, name="statistics"),
]
