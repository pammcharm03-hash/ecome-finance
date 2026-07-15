from django.urls import path
from payments import views

app_name = "payments"

urlpatterns = [
    path("search/", views.payment_search, name="payment_search"),
    path("process/<int:student_pk>/", views.payment_process, name="payment_process"),
    path("status/<int:pk>/", views.payment_status, name="payment_status"),
    path("history/", views.payment_history, name="payment_history"),
    path("receipt/<int:pk>/", views.receipt_view, name="receipt_view"),
    path("webhook/", views.webhook, name="webhook"),
    path("audit/", views.audit_log, name="audit_log"),
]
