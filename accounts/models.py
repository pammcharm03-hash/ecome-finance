from django.contrib.auth.models import AbstractUser
from django.db import models


class Branch(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Super Admin"
        REGISTRAR = "registrar", "Registrar"
        ACCOUNTANT = "accountant", "Accountant"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.ACCOUNTANT
    )
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    phone = models.CharField(max_length=20, blank=True)
    is_active_user = models.BooleanField(default=True)

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_registrar(self):
        return self.role == self.Role.REGISTRAR

    @property
    def is_accountant(self):
        return self.role == self.Role.ACCOUNTANT
