from django.db.models import Sum, Count, Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from accounts.models import Branch
from students.models import Student
from payments.models import Payment
from finance.models import FeeType


def _filter_by_branch(qs, user):
    if not user.is_admin and user.branch_id:
        return qs.filter(branch_id=user.branch_id)
    return qs


@login_required
def home(request):
    if request.user.is_admin:
        return admin_dashboard(request)
    if request.user.is_registrar:
        from django.shortcuts import redirect
        return redirect('students:student_list')
    if request.user.is_accountant:
        from django.shortcuts import redirect
        return redirect('payments:payment_search')
    return admin_dashboard(request)


@login_required
def admin_dashboard(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_start = today.replace(day=1)

    payments = _filter_by_branch(Payment.objects.all(), request.user)

    today_revenue = payments.filter(
        status=Payment.Status.SUCCESSFUL, created_at__date=today
    ).aggregate(total=Sum("amount"))["total"] or 0

    week_revenue = payments.filter(
        status=Payment.Status.SUCCESSFUL, created_at__date__gte=week_ago
    ).aggregate(total=Sum("amount"))["total"] or 0

    month_revenue = payments.filter(
        status=Payment.Status.SUCCESSFUL, created_at__date__gte=month_start
    ).aggregate(total=Sum("amount"))["total"] or 0

    total_students = _filter_by_branch(Student.objects.all(), request.user).count()

    total_payments = payments.count()
    successful = payments.filter(status=Payment.Status.SUCCESSFUL).count()
    failed = payments.filter(status=Payment.Status.FAILED).count()
    pending = payments.filter(status=Payment.Status.PENDING).count()

    # Revenue by fee type
    by_fee_type = payments.filter(
        status=Payment.Status.SUCCESSFUL
    ).values("fee_type__name").annotate(
        total=Sum("amount")
    ).order_by("-total")

    # Revenue by branch (admin only)
    by_branch = []
    if request.user.is_admin:
        by_branch = payments.filter(
            status=Payment.Status.SUCCESSFUL
        ).values("branch__name").annotate(
            total=Sum("amount")
        ).order_by("-total")

    # Recent transactions
    recent = payments.select_related("student", "fee_type", "branch").all()[:10]

    # Revenue by class
    by_class = payments.filter(
        status=Payment.Status.SUCCESSFUL
    ).values("student__school_class__name").annotate(
        total=Sum("amount")
    ).order_by("-total")[:10]

    context = {
        "today_revenue": today_revenue,
        "week_revenue": week_revenue,
        "month_revenue": month_revenue,
        "total_students": total_students,
        "total_payments": total_payments,
        "successful": successful,
        "failed": failed,
        "pending": pending,
        "by_fee_type": list(by_fee_type),
        "by_branch": list(by_branch),
        "by_class": list(by_class),
        "recent": recent,
        "branches": Branch.objects.all(),
    }
    return render(request, "dashboard/admin_dashboard.html", context)
