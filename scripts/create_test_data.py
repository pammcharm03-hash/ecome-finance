from accounts.models import Branch, User
from academics.models import Level, SchoolClass, AcademicYear, Term
from finance.models import FeeType, FeeAssignment
from students.models import Student
from payments.models import Payment
from django.utils import timezone

# Branch
branch, _ = Branch.objects.get_or_create(code='MAIN', defaults={'name': 'Main Branch', 'address': '123 Main St', 'phone': '000-000-0000'})
print('Branch:', branch)

# Users
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(username='admin', email='admin@example.com', password='AdminPass123!')
    print('Created superuser admin')
else:
    print('Admin exists')

# Level and class
level, _ = Level.objects.get_or_create(code='P1', defaults={'name': 'Primary 1', 'order': 1})
school_class, _ = SchoolClass.objects.get_or_create(code='P1A', defaults={'name': 'Primary 1 - A', 'level': level, 'branch': branch})
print('Level:', level)
print('Class:', school_class)

# Academic year and term
ay, _ = AcademicYear.objects.get_or_create(name='2026', defaults={'start_date': '2026-01-01', 'end_date': '2026-12-31', 'is_active': True})
term, _ = Term.objects.get_or_create(
    name='Term 1', academic_year=ay,
    defaults={'number': 1, 'is_active': True, 'start_date': '2026-01-01', 'end_date': '2026-04-30'}
)
print('AcademicYear:', ay)
print('Term:', term)

# Fee type and assignment
fee_type, _ = FeeType.objects.get_or_create(name='Tuition', defaults={'description': 'Monthly tuition fee'})
fee_assignment, _ = FeeAssignment.objects.get_or_create(
    fee_type=fee_type, academic_year=ay, scope='school', defaults={'amount': 50000}
)
print('FeeType:', fee_type)
print('FeeAssignment:', fee_assignment)

# Student
student, created = Student.objects.get_or_create(
    student_id='S1001', defaults={'first_name': 'John', 'last_name': 'Doe', 'gender': 'M', 'branch': branch, 'level': level, 'school_class': school_class, 'parent_phone': '0123456789'}
)
print('Student:', student, 'Created:', created)

# Payment
payment, created = Payment.objects.get_or_create(
    student=student, fee_type=fee_type, amount=50000, branch=branch, defaults={'parent_phone': student.parent_phone, 'accountant': None}
)
print('Payment:', payment, 'Created:', created)

print('\nTest data creation complete.')
