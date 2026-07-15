from django.contrib import admin
from finance.models import FeeType, FeeAssignment


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(FeeAssignment)
class FeeAssignmentAdmin(admin.ModelAdmin):
    list_display = ("fee_type", "amount", "scope", "academic_year", "term", "branch", "level", "school_class")
    list_filter = ("scope", "academic_year", "branch", "level")
