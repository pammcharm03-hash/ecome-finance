from datetime import date

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from academics.models import AcademicYear, Term
from finance.models import FeeAssignment, FeeType


class AssignmentCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="secret123",
            role=User.Role.ADMIN,
        )
        self.fee_type = FeeType.objects.create(name="Tuition")
        self.academic_year = AcademicYear.objects.create(
            name="2025/2026",
            start_date=date(2025, 1, 1),
            end_date=date(2026, 12, 31),
            is_active=True,
        )
        self.term = Term.objects.create(
            academic_year=self.academic_year,
            name="Term 1",
            number=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 3, 31),
            is_active=True,
        )

    def test_create_assignment_with_blank_optional_foreign_keys(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("finance:assignment_create"),
            {
                "fee_type": self.fee_type.pk,
                "amount": "50000",
                "scope": "school",
                "academic_year": self.academic_year.pk,
                "term": "",
                "branch": "",
                "level": "",
                "school_class": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(FeeAssignment.objects.filter(fee_type=self.fee_type).exists())
