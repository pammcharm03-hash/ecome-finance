from django.urls import path
from payments import views

app_name = "payments"

urlpatterns = [
    path("search/", views.payment_search, name="payment_search"),
    path("process/<int:student_pk>/", views.payment_process, name="payment_process"),
    path("status/<int:pk>/", views.payment_status, name="payment_status"),
    path("status/<int:pk>/api/", views.payment_status_api, name="payment_status_api"),
    path("verify/<int:pk>/", views.payment_verify, name="payment_verify"),
    path("cancel/<int:pk>/", views.payment_cancel, name="payment_cancel"),
    path("history/", views.payment_history, name="payment_history"),
    path("receipt/<int:pk>/", views.receipt_view, name="receipt_view"),
    path("webhook/", views.webhook, name="webhook"),
    path("audit/", views.audit_log, name="audit_log"),
]
