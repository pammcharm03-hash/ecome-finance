import uuid
from django.db import models
from django.utils import timezone
from accounts.models import User, Branch
from students.models import Student
from finance.models import FeeType, FeeAssignment


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESSFUL = "successful", "Successful"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name="payments")
    fee_type = models.ForeignKey(FeeType, on_delete=models.PROTECT, related_name="payments")
    fee_assignment = models.ForeignKey(
        FeeAssignment, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    parent_phone = models.CharField(max_length=20)
    transaction_ref = models.CharField(max_length=100, blank=True)
    paypack_ref = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    accountant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="payments")
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="payments")
    failure_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["branch", "created_at"]),
            models.Index(fields=["student"]),
        ]

    def __str__(self):
        return f"{self.receipt_number or 'N/A'} - {self.student} - {self.amount} RWF"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_logs")
    action = models.CharField(max_length=100)
    detail = models.TextField(blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} by {self.user} at {self.created_at:%Y-%m-%d %H:%M}"
