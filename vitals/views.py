from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import VitalsRecord
from .forms import VitalsForm
from patients.models import Patient


@login_required
def create(request):
    patient_id = request.GET.get("patient")
    patient = None
    if patient_id:
        patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == "POST":
        form = VitalsForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, "Vitals recorded successfully.")
            return redirect("patients:profile", pk=record.patient.id)
    else:
        form = VitalsForm(initial={"patient": patient.id} if patient else {})

    return render(request, "vitals/create.html", {"form": form, "patient": patient})


@login_required
def edit(request, pk):
    record = get_object_or_404(VitalsRecord, pk=pk)

    if not record.is_editable and not request.user.is_unit_head():
        messages.error(request, "This record can no longer be edited. Please request a correction.")
        return redirect("patients:profile", pk=record.patient.id)

    if request.method == "POST":
        form = VitalsForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Vitals updated successfully.")
            return redirect("patients:profile", pk=record.patient.id)
    else:
        form = VitalsForm(instance=record)

    return render(request, "vitals/edit.html", {"form": form, "record": record})


@login_required
@require_http_methods(["POST"])
def request_correction(request, pk):
    record = get_object_or_404(VitalsRecord, pk=pk)
    reason = request.POST.get("reason", "")
    record.correction_requested = True
    record.correction_reason = reason
    record.save()
    messages.success(request, "Correction request submitted.")
    return redirect("patients:profile", pk=record.patient.id)
