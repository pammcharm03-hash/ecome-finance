from django.urls import path
from reports import views

app_name = "reports"

urlpatterns = [
    path("", views.home, name="home"),
    path("export/students/", views.export_students, name="export_students"),
    path("export/payments/", views.export_payments, name="export_payments"),
]
