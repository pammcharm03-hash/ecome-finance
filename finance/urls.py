from django.urls import path
from finance import views

app_name = "finance"

urlpatterns = [
    path("fee-types/", views.feetype_list, name="feetype_list"),
    path("fee-types/new/", views.feetype_create, name="feetype_create"),
    path("fee-types/<int:pk>/edit/", views.feetype_edit, name="feetype_edit"),
    path("assignments/", views.assignment_list, name="assignment_list"),
    path("assignments/new/", views.assignment_create, name="assignment_create"),
    path("assignments/<int:pk>/delete/", views.assignment_delete, name="assignment_delete"),
]
