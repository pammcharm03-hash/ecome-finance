from django.db import models
from accounts.models import Branch
from academics.models import Level, SchoolClass, AcademicYear, Term


class FeeType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class FeeAssignment(models.Model):
    class Scope(models.TextChoices):
        WHOLE_SCHOOL = "school", "Whole School"
        BRANCH = "branch", "Branch"
        LEVEL = "level", "Level"
        CLASS = "class", "Class"

    fee_type = models.ForeignKey(FeeType, on_delete=models.PROTECT, related_name="assignments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    scope = models.CharField(max_length=10, choices=Scope.choices)
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name="fee_assignments"
    )
    term = models.ForeignKey(
        Term, on_delete=models.PROTECT, related_name="fee_assignments", null=True, blank=True
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.PROTECT, null=True, blank=True, related_name="fee_assignments"
    )
    level = models.ForeignKey(
        Level, on_delete=models.PROTECT, null=True, blank=True, related_name="fee_assignments"
    )
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.PROTECT, null=True, blank=True, related_name="fee_assignments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fee_type__name"]
        unique_together = ("fee_type", "academic_year", "term", "scope", "branch", "level", "school_class")

    def __str__(self):
        return f"{self.fee_type.name} - {self.amount} RWF ({self.get_scope_display()})"

    def applies_to_class(self, school_class):
        if self.scope == self.Scope.WHOLE_SCHOOL:
            return True
        if self.scope == self.Scope.BRANCH:
            return self.branch_id == school_class.branch_id
        if self.scope == self.Scope.LEVEL:
            return self.level_id == school_class.level_id
        if self.scope == self.Scope.CLASS:
            return self.school_class_id == school_class.id
        return False
