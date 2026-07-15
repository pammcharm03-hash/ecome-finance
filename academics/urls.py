from django.urls import path
from academics import views

app_name = "academics"

urlpatterns = [
    path("levels/", views.level_list, name="level_list"),
    path("levels/new/", views.level_create, name="level_create"),
    path("levels/<int:pk>/edit/", views.level_edit, name="level_edit"),
    path("classes/", views.class_list, name="class_list"),
    path("classes/new/", views.class_create, name="class_create"),
    path("classes/<int:pk>/edit/", views.class_edit, name="class_edit"),
    path("years/", views.year_list, name="year_list"),
    path("years/new/", views.year_create, name="year_create"),
    path("years/<int:year_pk>/terms/new/", views.term_create, name="term_create"),
]
