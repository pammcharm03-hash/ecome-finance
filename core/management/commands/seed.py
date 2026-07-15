"""Seed command: clean the database and create the default admin user.

Run with:  python manage.py seed

This wipes all operational data and leaves only a single superuser
(username: admin / password: admin) so the app always starts from a clean,
predictable state.
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection

from accounts.models import User as AccountUser, Branch
from students.models import Student
from academics.models import Level, SchoolClass, AcademicYear, Term
from finance.models import FeeType, FeeAssignment
from payments.models import Payment, AuditLog


class Command(BaseCommand):
    help = "Clean the database and create the default admin/admin user."

    def handle(self, *args, **options):
        # Delete in FK-safe order.
        Payment.objects.all().delete()
        AuditLog.objects.all().delete()
        FeeAssignment.objects.all().delete()
        Student.objects.all().delete()
        SchoolClass.objects.all().delete()
        Term.objects.all().delete()
        AcademicYear.objects.all().delete()
        Level.objects.all().delete()
        FeeType.objects.all().delete()
        Branch.objects.all().delete()

        # Remove every user except the one we are about to (re)create.
        AccountUser.objects.all().delete()

        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@ecome.rw",
                password="admin",
            )
            self.stdout.write(self.style.SUCCESS("Created admin user (admin/admin)."))
        else:
            self.stdout.write("Admin user already exists.")

        self.stdout.write(self.style.SUCCESS("Database seeded and cleaned successfully."))