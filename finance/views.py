from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Branch
from academics.models import Level, SchoolClass, AcademicYear, Term
from finance.models import FeeType, FeeAssignment


def is_admin(user):
    return user.is_authenticated and user.is_admin


# --- Fee Types ---

@login_required
@user_passes_test(is_admin)
def feetype_list(request):
    fee_types = FeeType.objects.all()
    return render(request, "finance/feetype_list.html", {"fee_types": fee_types})


@login_required
@user_passes_test(is_admin)
def feetype_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        if name:
            FeeType.objects.create(name=name, description=description)
            messages.success(request, "Fee type created.")
            return redirect("finance:feetype_list")
        messages.error(request, "Name required.")
    return render(request, "finance/feetype_form.html", {"title": "Add Fee Type"})


@login_required
@user_passes_test(is_admin)
def feetype_edit(request, pk):
    ft = get_object_or_404(FeeType, pk=pk)
    if request.method == "POST":
        ft.name = request.POST.get("name", ft.name).strip()
        ft.description = request.POST.get("description", "").strip()
        ft.save()
        messages.success(request, "Fee type updated.")
        return redirect("finance:feetype_list")
    return render(request, "finance/feetype_form.html", {"fee_type": ft, "title": "Edit Fee Type"})


@login_required
@user_passes_test(is_admin)
def feetype_delete(request, pk):
    ft = get_object_or_404(FeeType, pk=pk)
    if request.method == "POST":
        name = ft.name
        ft.delete()
        messages.success(request, f"Fee type '{name}' deleted.")
        return redirect("finance:feetype_list")
    return render(request, "finance/confirm_delete.html", {"object": ft, "type": "Fee Type", "cancel_url": "finance:feetype_list"})


# --- Fee Assignments ---

@login_required
@user_passes_test(is_admin)
def assignment_list(request):
    assignments = FeeAssignment.objects.select_related(
        "fee_type", "academic_year", "term", "branch", "level", "school_class"
    ).all()
    return render(request, "finance/assignment_list.html", {"assignments": assignments})


@login_required
@user_passes_test(is_admin)
def assignment_create(request):
    fee_types = FeeType.objects.all()
    years = AcademicYear.objects.all()
    terms = Term.objects.all()
    branches = Branch.objects.all()
    levels = Level.objects.all()
    classes = SchoolClass.objects.select_related("level", "branch").all()

    if request.method == "POST":
        fee_type_id = request.POST.get("fee_type")
        amount = request.POST.get("amount")
        scope = request.POST.get("scope")
        year_id = request.POST.get("academic_year")
        term_id = request.POST.get("term")
        branch_id = request.POST.get("branch")
        level_id = request.POST.get("level")
        class_id = request.POST.get("school_class")

        fee_type = FeeType.objects.filter(pk=fee_type_id).first()
        year = AcademicYear.objects.filter(pk=year_id).first()
        term = Term.objects.filter(pk=term_id).first() if term_id else None
        branch = Branch.objects.filter(pk=branch_id).first() if branch_id else None
        level = Level.objects.filter(pk=level_id).first() if level_id else None
        school_class = SchoolClass.objects.filter(pk=class_id).first() if class_id else None

        if not fee_type or not amount or not scope or not year:
            messages.error(request, "Fee type, amount, scope, and academic year are required.")
            return render(request, "finance/assignment_form.html", {
                "fee_types": fee_types, "years": years, "terms": terms,
                "branches": branches, "levels": levels, "classes": classes, "title": "Add Fee Assignment"
            })

        assignment = FeeAssignment.objects.create(
            fee_type=fee_type,
            amount=Decimal(amount),
            scope=scope,
            academic_year=year,
            term=term,
            branch=branch,
            level=level,
            school_class=school_class,
        )
        messages.success(request, f"Fee assignment created: {assignment}")
        return redirect("finance:assignment_list")

    return render(request, "finance/assignment_form.html", {
        "fee_types": fee_types, "years": years, "terms": terms,
        "branches": branches, "levels": levels, "classes": classes, "title": "Add Fee Assignment"
    })


@login_required
@user_passes_test(is_admin)
def assignment_delete(request, pk):
    assignment = get_object_or_404(FeeAssignment, pk=pk)
    if request.method == "POST":
        assignment.delete()
        messages.success(request, "Fee assignment deleted.")
    return redirect("finance:assignment_list")
