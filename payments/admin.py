from django.contrib import admin
from payments.models import Payment, AuditLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "student", "fee_type", "amount", "status", "branch", "created_at")
    list_filter = ("status", "branch", "fee_type")
    search_fields = ("receipt_number", "transaction_ref", "student__student_id", "student__first_name")
    readonly_fields = ("receipt_number",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "branch", "created_at")
    list_filter = ("action", "branch")
    search_fields = ("action", "detail")
