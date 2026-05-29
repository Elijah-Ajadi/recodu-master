import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from accounts.models import User
from vitals.models import VitalsRecord
from patients.models import Patient


def is_unit_head(user):
    return user.is_authenticated and user.is_unit_head()


@login_required
@user_passes_test(is_unit_head)
def home(request):
    today = timezone.now().date()
    today_vitals = VitalsRecord.objects.filter(recorded_at__date=today)
    total_checked = today_vitals.count()
    high_risk = today_vitals.filter(
        Q(systolic__gte=140)
        | Q(diastolic__gte=90)
        | Q(temperature__gt=38.0)
        | Q(temperature__lt=36.1)
    ).count()
    correction_requests = VitalsRecord.objects.filter(correction_requested=True, correction_approved=False).order_by("-recorded_at")
    recent_vitals = VitalsRecord.objects.select_related("patient", "recorded_by").order_by("-recorded_at")[:10]

    return render(request, "dashboard/home.html", {
        "total_checked": total_checked,
        "high_risk": high_risk,
        "correction_requests": correction_requests,
        "recent_vitals": recent_vitals,
    })


@login_required
@user_passes_test(is_unit_head)
def users(request):
    all_users = User.objects.order_by("-date_joined")
    return render(request, "dashboard/users.html", {"users": all_users})


@login_required
@user_passes_test(is_unit_head)
def toggle_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account.")
    else:
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "deactivated"
        messages.success(request, f"User {user.username} has been {status}.")
    return redirect("dashboard:users")


@login_required
@user_passes_test(is_unit_head)
def approve_correction(request, pk):
    record = get_object_or_404(VitalsRecord, pk=pk)
    record.correction_approved = True
    record.correction_requested = False
    record.correction_reason = ""
    record.save()
    messages.success(request, "Correction approved. Record can now be edited.")
    return redirect("dashboard:home")


@login_required
@user_passes_test(is_unit_head)
def export(request):
    if request.method == "POST":
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        queryset = VitalsRecord.objects.select_related("patient", "recorded_by").order_by("-recorded_at")

        if start_date:
            queryset = queryset.filter(recorded_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(recorded_at__date__lte=end_date)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="recodu_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "Date", "Patient", "Phone", "Recorded By",
            "Systolic", "Diastolic", "Pulse", "Temperature",
            "Glucose Type", "Glucose Value", "Notes", "Medications"
        ])

        for v in queryset:
            writer.writerow([
                v.recorded_at.strftime("%Y-%m-%d %H:%M"),
                v.patient.full_name,
                v.patient.phone,
                v.recorded_by.username if v.recorded_by else "Unknown",
                v.systolic,
                v.diastolic,
                v.pulse,
                v.temperature,
                v.glucose_type,
                v.glucose_value,
                v.notes,
                v.medications,
            ])

        return response

    return render(request, "dashboard/export.html")

@login_required
@user_passes_test(is_unit_head)
def change_role(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user.id == request.user.id:
        messages.error(request, "You cannot change your own role.")
    else:
        user.role = "UNIT_HEAD" if user.role == "VOLUNTEER" else "VOLUNTEER"
        user.save()
        messages.success(request, f"User {user.username} is now a {user.get_role_display()}.")
    return redirect("dashboard:users")
