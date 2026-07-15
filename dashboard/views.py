import json
from django.db.models import Sum, Count, Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from accounts.models import Branch, User
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
        "fee_data_json": json.dumps(list(by_fee_type), ensure_ascii=False),
        "branch_data_json": json.dumps(list(by_branch), ensure_ascii=False),
        "class_data_json": json.dumps(list(by_class), ensure_ascii=False),
        "recent": recent,
        "branches": Branch.objects.all(),
        "total_users": User.objects.count(),
        "total_branches": Branch.objects.count(),
        "total_fee_types": FeeType.objects.count(),
        "quick_links": [
            {"label": "Branches", "url": "accounts:branch_list", "icon": "bi-building", "cls": "primary"},
            {"label": "Users", "url": "accounts:user_list", "icon": "bi-people", "cls": "success"},
            {"label": "Levels", "url": "academics:level_list", "icon": "bi-layers", "cls": "warning"},
            {"label": "Classes", "url": "academics:class_list", "icon": "bi-easel", "cls": "danger"},
            {"label": "Academic Years", "url": "academics:year_list", "icon": "bi-calendar3", "cls": "primary"},
            {"label": "Fee Types", "url": "finance:feetype_list", "icon": "bi-tag", "cls": "success"},
            {"label": "Fee Assignments", "url": "finance:assignment_list", "icon": "bi-clipboard-check", "cls": "warning"},
            {"label": "Students", "url": "students:student_list", "icon": "bi-mortarboard", "cls": "danger"},
            {"label": "Collect Payment", "url": "payments:payment_search", "icon": "bi-cash-coin", "cls": "primary"},
            {"label": "Payment History", "url": "payments:payment_history", "icon": "bi-receipt", "cls": "success"},
            {"label": "Reports", "url": "reports:home", "icon": "bi-file-earmark-spreadsheet", "cls": "warning"},
            {"label": "Audit Log", "url": "payments:audit_log", "icon": "bi-clock-history", "cls": "danger"},
        ],
    }
    return render(request, "dashboard/admin_dashboard.html", context)
