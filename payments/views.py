import json
import uuid
import re
import logging
from decimal import Decimal, InvalidOperation
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
from payments.paypack import (
    initiate_payment,
    parse_webhook_payload,
)
from payments.paypack import PaymentGatewayError as PaypackError

logger = logging.getLogger(__name__)
from django.conf import settings


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


def _validate_phone_number(phone):
    """Validate Rwanda mobile phone number format."""
    # Rwanda phone numbers: start with +250 or 250 or 07 or 06
    phone = re.sub(r'\s', '', str(phone).strip())
    # Normalize to 07/06 format if needed
    if phone.startswith('+250'):
        phone = '0' + phone[4:]
    elif phone.startswith('250'):
        phone = '0' + phone[3:]
    
    # Valid Rwanda formats: 07xxxxxxxx or 06xxxxxxxx
    if not re.match(r'^0[76]\d{8}$', phone):
        raise ValueError("Invalid Rwanda phone number format. Use 07xxxxxxxx or 06xxxxxxxx")
    return phone


def _validate_amount(amount_str):
    """Validate and convert amount to Decimal."""
    try:
        amount = Decimal(str(amount_str).strip())
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        if amount.as_tuple().exponent < -2:
            raise ValueError("Amount cannot have more than 2 decimal places")
        return amount
    except (InvalidOperation, ValueError) as e:
        raise ValueError(f"Invalid amount: {e}")


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
        
        # Validate amount
        try:
            amount_val = _validate_amount(amount)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("payments:payment_process", student.pk)

        if remaining > 0 and amount_val > Decimal(str(remaining)):
            messages.error(request, f"Amount exceeds remaining balance of {remaining} RWF.")
            return redirect("payments:payment_process", student.pk)

        # Validate phone number
        try:
            phone = _validate_phone_number(phone)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect("payments:payment_process", student.pk)

        # Create pending payment
        payment = Payment.objects.create(
            student=student,
            fee_type=fee_type,
            fee_assignment=fee_options.filter(fee_type=fee_type).first(),
            amount=float(amount_val),
            parent_phone=phone,
            status=Payment.Status.PENDING,
            accountant=request.user,
            branch=student.branch,
        )

        # Try to call HDEV
        try:
            callback_url = getattr(settings, "HDEV_WEBHOOK_URL", None)
            
            # Prepare metadata from database for tracking
            metadata = {
                "student_id": student.student_id,
                "student_name": student.full_name,
                "fee_type": fee_type.name,
                "branch": student.branch.name,
                "class": student.school_class.name if student.school_class else "N/A",
            }
            
            result = initiate_payment(
                phone_number=phone,
                amount=amount_val,
                reference=payment.receipt_number,
                description=f"{fee_type.name} - {student.full_name}",
                callback_url=callback_url,
                metadata=metadata,
            )
            # result contains: client_transaction_id, reference, status, amount, phone
            payment.transaction_ref = result.get("client_transaction_id") or result.get("reference", "")
            payment.paypack_ref = result.get("reference", "")
            payment.save()

            AuditLog.objects.create(
                user=request.user, action="Payment Initiated",
                detail=f"Payment {payment.receipt_number} for {student.full_name} - {fee_type.name} - {amount_val} RWF - Ref: {payment.transaction_ref}",
                branch=student.branch,
            )
            messages.success(request, f"✓ Payment request sent to {phone}. Parent will receive a Mobile Money prompt.")
            return redirect("payments:payment_status", payment.pk)

        except PaypackError as e:
            payment.status = Payment.Status.FAILED
            payment.failure_reason = str(e)
            payment.save()
            
            AuditLog.objects.create(
                user=request.user, action="Payment Failed",
                detail=f"Payment initiation failed: {str(e)}",
                branch=student.branch,
            )
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
def payment_verify(request, pk):
    """Manually poll HDEV for the latest transaction status (fallback to webhook)."""
    payment = get_object_or_404(Payment, pk=pk)
    if not request.user.is_admin and request.user.branch_id != payment.branch_id:
        messages.error(request, "Access denied.")
        return redirect("payments:payment_search")

    if payment.status == Payment.Status.SUCCESSFUL:
        return redirect("payments:payment_status", payment.pk)

    ref = payment.transaction_ref or payment.paypack_ref or payment.receipt_number
    try:
        data = get_transaction_status(ref)
        status = (data.get("status") or "").lower()
        if status in ("success", "successful", "completed"):
            payment.status = Payment.Status.SUCCESSFUL
            payment.completed_at = timezone.now()
            payment.save()
            AuditLog.objects.create(
                user=request.user, action="Payment Successful",
                detail=f"Payment {payment.receipt_number} confirmed via manual status check - {payment.amount} RWF",
                branch=payment.branch,
            )
            messages.success(request, "Payment confirmed as successful.")
        elif status in ("failed", "error", "declined", "cancelled", "canceled"):
            payment.status = Payment.Status.FAILED
            payment.failure_reason = "Payment declined or failed via HDEV"
            payment.save()
            messages.warning(request, "Payment was not successful.")
        else:
            messages.info(request, "Payment is still pending on HDEV.")
    except PaypackError as e:
        error_msg = str(e)
        if "404" in error_msg or "Not Found" in error_msg:
            messages.warning(request, "HDEV status lookup returned 404. The transaction may still be processing. Please wait for the webhook confirmation or check your HDEV dashboard.")
        else:
            messages.error(request, f"Could not verify payment: {e}")

    return redirect("payments:payment_status", payment.pk)


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
    """HDEV webhook endpoint for payment notifications."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    payload = parse_webhook_payload(request.body)
    if not payload:
        logger.warning("Webhook received invalid JSON payload")
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    logger.info(f"Webhook received: event={payload.get('event')}, status={payload.get('status')}, ref={payload.get('ref')}, external_ref={payload.get('external_reference')}")

    status = payload.get("status", "")
    ref = payload.get("ref", "")
    external_ref = payload.get("external_reference", "")
    client_transaction_id = payload.get("client_transaction_id", "")

    # Find payment by the reference we originally sent (receipt number) or by
    # HDEV's internal transaction id.
    payment = None
    for candidate in (external_ref, ref, client_transaction_id):
        if not candidate:
            continue
        payment = (
            Payment.objects.filter(receipt_number=candidate).first()
            or Payment.objects.filter(transaction_ref=candidate).first()
        )
        if payment:
            break

    if not payment:
        logger.warning(f"Webhook payment not found for candidates: external_ref={external_ref}, ref={ref}, client_transaction_id={client_transaction_id}")
        return JsonResponse({"status": "error", "message": "Payment not found"}, status=404)

    # Prevent double processing
    if payment.status == Payment.Status.SUCCESSFUL:
        logger.info(f"Webhook ignored: payment {payment.receipt_number} already successful")
        return JsonResponse({"status": "ok", "message": "Already processed"})

    if status in ("success", "successful", "completed"):
        payment.status = Payment.Status.SUCCESSFUL
        payment.transaction_ref = client_transaction_id or payment.transaction_ref
        payment.paypack_ref = ref or payment.paypack_ref
        payment.completed_at = timezone.now()
        payment.save()

        logger.info(f"Webhook marked payment {payment.receipt_number} as successful")

        AuditLog.objects.create(
            user=payment.accountant, action="Payment Successful",
            detail=f"Payment {payment.receipt_number} confirmed via webhook - {payment.amount} RWF",
            branch=payment.branch,
        )
    elif status in ("failed", "error", "declined", "cancelled", "canceled"):
        payment.status = Payment.Status.FAILED
        payment.failure_reason = "Payment declined or failed via HDEV"
        payment.save()

        logger.info(f"Webhook marked payment {payment.receipt_number} as failed")

        AuditLog.objects.create(
            user=payment.accountant, action="Payment Failed",
            detail=f"Payment {payment.receipt_number} failed - {payment.failure_reason}",
            branch=payment.branch,
        )
    else:
        # pending or unknown: leave as pending, just acknowledge receipt.
        logger.info(f"Webhook ignored status '{status}' for payment {payment.receipt_number}")
        return JsonResponse({"status": "ok", "message": f"Ignored status: {status}"})

    return JsonResponse({"status": "ok"})


@login_required
def payment_status_api(request, pk):
    """AJAX endpoint to get payment status (for real-time polling from UI)."""
    payment = get_object_or_404(Payment, pk=pk)
    if not request.user.is_admin and request.user.branch_id != payment.branch_id:
        return JsonResponse({"error": "Access denied"}, status=403)
    
    return JsonResponse({
        "status": payment.status,
        "receipt_number": payment.receipt_number,
        "student_name": payment.student.full_name,
        "fee_type": payment.fee_type.name,
        "amount": float(payment.amount),
        "phone": payment.parent_phone,
        "created_at": payment.created_at.isoformat(),
        "updated_at": payment.updated_at.isoformat(),
        "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
        "failure_reason": payment.failure_reason or "",
        "is_success": payment.status == Payment.Status.SUCCESSFUL,
        "is_pending": payment.status == Payment.Status.PENDING,
        "is_failed": payment.status == Payment.Status.FAILED,
    })


@login_required
def audit_log(request):
    """View audit logs (admin only)."""
    if not request.user.is_admin:
        messages.error(request, "Admin access only.")
        return redirect("dashboard:home")

    logs = AuditLog.objects.select_related("user", "branch").all()[:100]
    return render(request, "payments/audit_log.html", {"logs": logs})
