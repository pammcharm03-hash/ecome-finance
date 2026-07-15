from django.contrib import admin
from students.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("student_id", "first_name", "last_name", "branch", "level", "school_class", "status")
    list_filter = ("branch", "level", "status", "gender")
    search_fields = ("student_id", "first_name", "last_name", "parent_phone")
