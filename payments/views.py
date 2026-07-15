import json
import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from accounts.models import User
from students.models import Student
from finance.models import FeeType, FeeAssignment
from academics.models import AcademicYear
from payments.models import Payment, AuditLog
from payments.paypack import initiate_payment, PaypackError


def _filter_branch(qs, user):
    if not user.is_admin and user.branch_id:
        return qs.filter(branch_id=user.branch_id)
    return qs


def _get_fee_options(student):
    """Get fee assignments applicable to a student's class."""
    active_year = AcademicYear.objects.filter(is_active=True).first()
    if not active_year:
        return []
    return FeeAssignment.objects.filter(
        Q(scope="school") |
        Q(scope="branch", branch=student.branch) |
        Q(scope="level", level=student.level) |
        Q(scope="class", school_class=student.school_class)
    ).filter(academic_year=active_year).select_related("fee_type")


def _get_student_balance(student, fee_type):
    """Calculate remaining balance for a student and fee type."""
    active_year = AcademicYear.objects.filter(is_active=True).first()
    assignments = FeeAssignment.objects.filter(
        fee_type=fee_type,
        academic_year=active_year,
    ).filter(
        Q(scope="school") |
        Q(scope="branch", branch=student.branch) |
        Q(scope="level", level=student.level) |
        Q(scope="class", school_class=student.school_class)
    )
    required = sum(a.amount for a in assignments)
    paid = Payment.objects.filter(
        student=student, fee_type=fee_type,
        status=Payment.Status.SUCCESSFUL
    ).aggregate(total=Sum("amount"))["total"] or 0
    return required, paid, max(required - paid, 0)


@login_required
def payment_search(request):
    """Accountant searches for a student to collect payment."""
    if not request.user.is_accountant and not request.user.is_admin:
        messages.error(request, "You don't have permission to access payments.")
        return redirect("dashboard:home")

    students = _filter_branch(Student.objects.select_related("branch", "level", "school_class"), request.user)

    q = request.GET.get("q", "").strip()
    if q:
        students = students.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(student_id__icontains=q) |
            Q(parent_phone__icontains=q)
        )

    return render(request, "payments/payment_search.html", {
        "students": students[:20],
        "q": q,
    })


@login_required
def payment_process(request, student_pk):
    """Accountant selects fee type and enters payment details."""
    student = get_object_or_404(Student, pk=student_pk)

    # Branch check
    if not request.user.is_admin and request.user.branch_id != student.branch_id:
        messages.error(request, "Student not in your branch.")
        return redirect("payments:payment_search")

    fee_options = _get_fee_options(student)

    if request.method == "POST":
        fee_type_id = request.POST.get("fee_type")
        amount = request.POST.get("amount")
        phone = request.POST.get("phone", "").strip()

        fee_type = FeeType.objects.filter(pk=fee_type_id).first()
        if not fee_type:
            messages.error(request, "Please select a fee type.")
            return redirect("payments:payment_process", student.pk)

        required, paid, remaining = _get_student_balance(student, fee_type)
        try:
            amount_val = float(amount)
        except (TypeError, ValueError):
            messages.error(request, "Invalid amount.")
            return redirect("payments:payment_process", student.pk)

        if amount_val <= 0:
            messages.error(request, "Amount must be greater than zero.")
            return redirect("payments:payment_process", student.pk)

        if remaining > 0 and amount_val > remaining:
            messages.error(request, f"Amount exceeds remaining balance of {remaining} RWF.")
            return redirect("payments:payment_process", student.pk)

        if not phone:
            messages.error(request, "Phone number is required.")
            return redirect("payments:payment_process", student.pk)

        # Create pending payment
        payment = Payment.objects.create(
            student=student,
            fee_type=fee_type,
            fee_assignment=fee_options.filter(fee_type=fee_type).first(),
            amount=amount_val,
            parent_phone=phone,
            status=Payment.Status.PENDING,
            accountant=request.user,
            branch=student.branch,
        )

        # Try to call Paypack
        try:
            result = initiate_payment(
                phone_number=phone,
                amount=amount_val,
                reference=payment.receipt_number,
                description=f"{fee_type.name} - {student.full_name}"
            )
            payment.transaction_ref = result.get("reference", "") or result.get("transaction_ref", "")
            payment.paypack_ref = result.get("id", "")
            payment.save()

            AuditLog.objects.create(
                user=request.user, action="Payment Initiated",
                detail=f"Payment {payment.receipt_number} for {student.full_name} - {fee_type.name} - {amount_val} RWF",
                branch=student.branch,
            )
            messages.info(request, f"Payment request sent. Parent will receive a Mobile Money prompt on {phone}. Waiting for confirmation...")
            return redirect("payments:payment_status", payment.pk)

        except PaypackError as e:
            payment.status = Payment.Status.FAILED
            payment.failure_reason = str(e)
            payment.save()
            messages.error(request, f"Payment failed: {e}")
            return redirect("payments:payment_status", payment.pk)

    # GET: show form
    fee_choices = []
    for fa in fee_options:
        required, paid, remaining = _get_student_balance(student, fa.fee_type)
        fee_choices.append({
            "fee_type": fa.fee_type,
            "fee_type_id": fa.fee_type_id,
            "required": required,
            "paid": paid,
            "remaining": remaining,
        })

    if not fee_choices:
        for fee_type in FeeType.objects.all():
            fee_choices.append({
                "fee_type": fee_type,
                "fee_type_id": fee_type.pk,
                "required": 0,
                "paid": 0,
                "remaining": 0,
            })

    return render(request, "payments/payment_process.html", {
        "student": student,
        "fee_choices": fee_choices,
    })


@login_required
def payment_status(request, pk):
    """Show payment status after processing."""
    payment = get_object_or_404(Payment.objects.select_related("student", "fee_type", "branch"), pk=pk)
    if not request.user.is_admin and request.user.branch_id != payment.branch_id:
        messages.error(request, "Access denied.")
        return redirect("payments:payment_search")
    return render(request, "payments/payment_status.html", {"payment": payment})


@login_required
def payment_history(request):
    """View payment history."""
    payments = _filter_branch(
        Payment.objects.select_related("student", "fee_type", "branch", "accountant"),
        request.user
    )

    q = request.GET.get("q", "").strip()
    if q:
        payments = payments.filter(
            Q(receipt_number__icontains=q) |
            Q(transaction_ref__icontains=q) |
            Q(student__first_name__icontains=q) |
            Q(student__last_name__icontains=q)
        )

    status = request.GET.get("status")
    if status:
        payments = payments.filter(status=status)

    return render(request, "payments/payment_history.html", {
        "payments": payments[:50],
        "q": q,
        "status_filter": status,
    })


@login_required
def receipt_view(request, pk):
    """View/print a receipt."""
    payment = get_object_or_404(Payment.objects.select_related("student", "fee_type", "branch", "accountant"), pk=pk)
    if not request.user.is_admin and request.user.branch_id != payment.branch_id:
        messages.error(request, "Access denied.")
        return redirect("payments:payment_search")
    return render(request, "payments/receipt.html", {"payment": payment})


@csrf_exempt
def webhook(request):
    """Paypack webhook endpoint for payment notifications."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    # Extract transaction info from webhook
    transaction_ref = data.get("reference") or data.get("reference_number", "")
    paypack_ref = data.get("id") or data.get("transaction_id", "")
    status = data.get("status", "").lower()
    amount = data.get("amount", 0)

    # Find payment by receipt number (used as reference)
    payment = Payment.objects.filter(receipt_number=transaction_ref).first()
    if not payment:
        payment = Payment.objects.filter(transaction_ref=transaction_ref).first()

    if not payment:
        return JsonResponse({"status": "error", "message": "Payment not found"}, status=404)

    # Prevent double processing
    if payment.status == Payment.Status.SUCCESSFUL:
        return JsonResponse({"status": "ok", "message": "Already processed"})

    if status in ("success", "successful", "completed"):
        payment.status = Payment.Status.SUCCESSFUL
        payment.paypack_ref = paypack_ref
        payment.completed_at = timezone.now()
        payment.save()

        AuditLog.objects.create(
            user=payment.accountant, action="Payment Successful",
            detail=f"Payment {payment.receipt_number} confirmed via webhook - {payment.amount} RWF",
            branch=payment.branch,
        )
    elif status in ("failed", "error", "declined"):
        payment.status = Payment.Status.FAILED
        payment.failure_reason = data.get("message", data.get("reason", "Payment declined"))
        payment.save()

        AuditLog.objects.create(
            user=payment.accountant, action="Payment Failed",
            detail=f"Payment {payment.receipt_number} failed - {payment.failure_reason}",
            branch=payment.branch,
        )

    return JsonResponse({"status": "ok"})


@login_required
def audit_log(request):
    """View audit logs (admin only)."""
    if not request.user.is_admin:
        messages.error(request, "Admin access only.")
        return redirect("dashboard:home")

    logs = AuditLog.objects.select_related("user", "branch").all()[:100]
    return render(request, "payments/audit_log.html", {"logs": logs})
