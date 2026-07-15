from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.models import User, Branch


def _home_for_user(user):
    if user.is_admin:
        return "dashboard:admin_dashboard"
    if user.is_registrar:
        return "students:student_list"
    if user.is_accountant:
        return "payments:payment_search"
    return "dashboard:admin_dashboard"


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_home_for_user(request.user))
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            return redirect(_home_for_user(user))
        messages.error(request, "Invalid username or password.")
    return render(request, "registration/login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    # Redirect to the accounts app login view (namespaced)
    return redirect("accounts:login")


def is_admin(user):
    return user.is_authenticated and user.is_admin


@login_required
@user_passes_test(is_admin)
def branch_list(request):
    branches = Branch.objects.all()
    return render(request, "accounts/branch_list.html", {"branches": branches})


@login_required
@user_passes_test(is_admin)
def branch_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        address = request.POST.get("address", "").strip()
        phone = request.POST.get("phone", "").strip()
        if name and code:
            Branch.objects.create(name=name, code=code, address=address, phone=phone)
            messages.success(request, f"Branch '{name}' created.")
            return redirect("accounts:branch_list")
        messages.error(request, "Name and code are required.")
    return render(request, "accounts/branch_form.html", {"title": "Add Branch"})


@login_required
@user_passes_test(is_admin)
def branch_edit(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == "POST":
        branch.name = request.POST.get("name", branch.name).strip()
        branch.code = request.POST.get("code", branch.code).strip()
        branch.address = request.POST.get("address", "").strip()
        branch.phone = request.POST.get("phone", "").strip()
        branch.save()
        messages.success(request, "Branch updated.")
        return redirect("accounts:branch_list")
    return render(request, "accounts/branch_form.html", {"branch": branch, "title": "Edit Branch"})


@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.select_related("branch").all()
    return render(request, "accounts/user_list.html", {"users": users})


@login_required
@user_passes_test(is_admin)
def user_create(request):
    branches = Branch.objects.all()
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        role = request.POST.get("role", User.Role.ACCOUNTANT)
        branch_id = request.POST.get("branch")
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "accounts/user_form.html", {"branches": branches, "title": "Add User"})

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "accounts/user_form.html", {"branches": branches, "title": "Add User"})

        branch = Branch.objects.filter(pk=branch_id).first()
        if role != User.Role.ADMIN and not branch:
            messages.error(request, "Non-admin users must be assigned a branch.")
            return render(request, "accounts/user_form.html", {"branches": branches, "title": "Add User"})

        User.objects.create_user(
            username=username, password=password, first_name=first_name,
            last_name=last_name, email=email, phone=phone, role=role,
            branch=branch if role != User.Role.ADMIN else None,
        )
        messages.success(request, f"User '{username}' created.")
        return redirect("accounts:user_list")

    return render(request, "accounts/user_form.html", {"branches": branches, "title": "Add User"})


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    branches = Branch.objects.all()
    if request.method == "POST":
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.email = request.POST.get("email", "").strip()
        user.phone = request.POST.get("phone", "").strip()
        user.role = request.POST.get("role", user.role)
        branch_id = request.POST.get("branch")
        user.branch = Branch.objects.filter(pk=branch_id).first() if user.role != User.Role.ADMIN else None
        user.is_active = request.POST.get("is_active") == "on"
        new_password = request.POST.get("password", "").strip()
        if new_password:
            user.set_password(new_password)
        user.save()
        messages.success(request, "User updated.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_form.html", {"user": user, "branches": branches, "title": "Edit User"})


@login_required
@user_passes_test(is_admin)
def branch_delete(request, pk):
    branch = get_object_or_404(Branch, pk=pk)
    if request.method == "POST":
        name = branch.name
        branch.delete()
        messages.success(request, f"Branch '{name}' deleted.")
        return redirect("accounts:branch_list")
    return render(request, "accounts/branch_confirm_delete.html", {"branch": branch})


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.username == "admin":
        messages.error(request, "The default admin user cannot be deleted.")
        return redirect("accounts:user_list")
    if request.method == "POST":
        uname = user.username
        user.delete()
        messages.success(request, f"User '{uname}' deleted.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_confirm_delete.html", {"object": user, "type": "user"})
