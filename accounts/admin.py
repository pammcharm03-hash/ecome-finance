from django.contrib import admin
from accounts.models import User, Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "address", "phone")
    search_fields = ("name", "code")


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "get_full_name", "role", "branch", "is_active")
    list_filter = ("role", "branch", "is_active")
    search_fields = ("username", "first_name", "last_name")
