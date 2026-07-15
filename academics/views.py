from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import Branch
from academics.models import Level, SchoolClass, AcademicYear, Term


def is_admin(user):
    return user.is_authenticated and user.is_admin


# --- Levels ---

@login_required
@user_passes_test(is_admin)
def level_list(request):
    levels = Level.objects.all()
    return render(request, "academics/level_list.html", {"levels": levels})


@login_required
@user_passes_test(is_admin)
def level_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        order = request.POST.get("order", 0)
        if name and code:
            Level.objects.create(name=name, code=code, order=order)
            messages.success(request, "Level created.")
            return redirect("academics:level_list")
        messages.error(request, "Name and code required.")
    return render(request, "academics/level_form.html", {"title": "Add Level"})


@login_required
@user_passes_test(is_admin)
def level_edit(request, pk):
    level = get_object_or_404(Level, pk=pk)
    if request.method == "POST":
        level.name = request.POST.get("name", level.name).strip()
        level.code = request.POST.get("code", level.code).strip()
        level.order = request.POST.get("order", level.order)
        level.save()
        messages.success(request, "Level updated.")
        return redirect("academics:level_list")
    return render(request, "academics/level_form.html", {"level": level, "title": "Edit Level"})


# --- Classes ---

@login_required
@user_passes_test(is_admin)
def class_list(request):
    classes = SchoolClass.objects.select_related("level", "branch").all()
    return render(request, "academics/class_list.html", {"classes": classes})


@login_required
@user_passes_test(is_admin)
def class_create(request):
    levels = Level.objects.all()
    branches = Branch.objects.all()
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        level_id = request.POST.get("level")
        branch_id = request.POST.get("branch")
        level = Level.objects.filter(pk=level_id).first()
        branch = Branch.objects.filter(pk=branch_id).first()
        if name and level:
            SchoolClass.objects.create(name=name, code=code, level=level, branch=branch)
            messages.success(request, "Class created.")
            return redirect("academics:class_list")
        messages.error(request, "Name and level required.")
    return render(request, "academics/class_form.html", {"levels": levels, "branches": branches, "title": "Add Class"})


@login_required
@user_passes_test(is_admin)
def class_edit(request, pk):
    school_class = get_object_or_404(SchoolClass, pk=pk)
    levels = Level.objects.all()
    branches = Branch.objects.all()
    if request.method == "POST":
        school_class.name = request.POST.get("name", school_class.name).strip()
        school_class.code = request.POST.get("code", school_class.code).strip()
        school_class.level = Level.objects.filter(pk=request.POST.get("level")).first() or school_class.level
        school_class.branch = Branch.objects.filter(pk=request.POST.get("branch")).first()
        school_class.save()
        messages.success(request, "Class updated.")
        return redirect("academics:class_list")
    return render(request, "academics/class_form.html", {"class": school_class, "levels": levels, "branches": branches, "title": "Edit Class"})


# --- Academic Years ---

@login_required
@user_passes_test(is_admin)
def year_list(request):
    years = AcademicYear.objects.prefetch_related("terms").all()
    return render(request, "academics/year_list.html", {"years": years})


@login_required
@user_passes_test(is_admin)
def year_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active") == "on"
        if name and start_date and end_date:
            if is_active:
                AcademicYear.objects.filter(is_active=True).update(is_active=False)
            AcademicYear.objects.create(name=name, start_date=start_date, end_date=end_date, is_active=is_active)
            messages.success(request, "Academic year created.")
            return redirect("academics:year_list")
        messages.error(request, "All fields required.")
    return render(request, "academics/year_form.html", {"title": "Add Academic Year"})


@login_required
@user_passes_test(is_admin)
def term_create(request, year_pk):
    year = get_object_or_404(AcademicYear, pk=year_pk)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        number = request.POST.get("number")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active") == "on"
        if name and number and start_date and end_date:
            if is_active:
                Term.objects.filter(academic_year=year, is_active=True).update(is_active=False)
            Term.objects.create(
                academic_year=year, name=name, number=number,
                start_date=start_date, end_date=end_date, is_active=is_active
            )
            messages.success(request, "Term created.")
        return redirect("academics:year_list")
    return render(request, "academics/term_form.html", {"year": year, "title": "Add Term"})
