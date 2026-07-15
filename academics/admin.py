from django.contrib import admin
from academics.models import Level, AcademicYear, Term, SchoolClass


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "order")
    search_fields = ("name", "code")


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "level", "branch")
    list_filter = ("level", "branch")
    search_fields = ("name", "code")


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active")
    list_filter = ("is_active",)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "number", "is_active")
    list_filter = ("academic_year", "is_active")
