from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import User


@login_required
@require_http_methods(["GET", "POST"])
def reset_volunteer_password(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied

    volunteer = get_object_or_404(
        User,
        pk=pk,
        role="VOLUNTEER",
        is_superuser=False,
    )
    form = SetPasswordForm(volunteer, request.POST or None)
    for field in form.fields.values():
        field.widget.attrs["class"] = "form-input"

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            f"Password updated successfully for volunteer {volunteer.username}.",
        )
        return redirect("dashboard:users")

    return render(
        request,
        "dashboard/reset_volunteer_password.html",
        {"form": form, "volunteer": volunteer},
    )
