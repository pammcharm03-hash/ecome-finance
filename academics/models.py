from django.db import models
from django.core.validators import RegexValidator
from accounts.models import Branch


class Level(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=20, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-name"]

    def __str__(self):
        return self.name


class Term(models.Model):
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.CASCADE, related_name="terms"
    )
    name = models.CharField(max_length=50)
    number = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["academic_year", "number"]
        unique_together = ("academic_year", "number")

    def __str__(self):
        return f"{self.academic_year} - {self.name}"


class SchoolClass(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name="classes")
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name="classes", null=True, blank=True
    )

    class Meta:
        ordering = ["level__order", "name"]
        unique_together = ("name", "branch")

    def __str__(self):
        return f"{self.name} ({self.level.name})"
