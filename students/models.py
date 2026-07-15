from django.db import models
from django.core.validators import RegexValidator
from accounts.models import Branch
from academics.models import Level, SchoolClass, AcademicYear, Term


class Student(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"

    student_id = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    date_of_birth = models.DateField(null=True, blank=True)
    parent_name = models.CharField(max_length=150, blank=True)
    parent_phone = models.CharField(max_length=20, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name="students")
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name="students")
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.PROTECT, related_name="students"
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name="students", null=True
    )
    status = models.CharField(max_length=20, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student_id"]),
            models.Index(fields=["branch", "school_class"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
