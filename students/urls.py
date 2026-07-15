from django.urls import path
from students import views

app_name = "students"

urlpatterns = [
    path("", views.student_list, name="student_list"),
    path("new/", views.student_create, name="student_create"),
    path("import/", views.student_import, name="student_import"),
    path("export/", views.student_export, name="student_export"),
    path("template/", views.student_template, name="student_template"),
    path("<int:pk>/", views.student_detail, name="student_detail"),
    path("<int:pk>/edit/", views.student_edit, name="student_edit"),
]
