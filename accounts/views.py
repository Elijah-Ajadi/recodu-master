from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import LoginForm, UserRegistrationForm
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_unit_head():
            return redirect("dashboard:home")
        return redirect("patients:search")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_unit_head():
                return redirect("dashboard:home")
            return redirect("patients:search")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def register_volunteer(request):
    if not request.user.is_unit_head():
        messages.error(request, "You do not have permission to register users.")
        return redirect("patients:search")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User registered successfully.")
            return redirect("dashboard:users")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/register.html", {"form": form})
