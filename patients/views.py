import json
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from .models import Patient
from .forms import PatientRegistrationForm


@login_required
def search(request):
    return render(request, "patients/search.html")


@login_required
def ajax_search(request):
    query = request.GET.get("q", "").strip()
    if len(query) < 2:
        return JsonResponse({"results": []})

    results = Patient.objects.filter(
        Q(first_name__icontains=query)
        | Q(last_name__icontains=query)
        | Q(phone__icontains=query)
    )[:10]

    data = [
        {
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "phone": p.phone,
            "url": f"/patients/{p.id}/",
        }
        for p in results
    ]

    return JsonResponse({"results": data})


@login_required
def create(request):
    if request.method == "POST":
        data = json.loads(request.body)
        form = PatientRegistrationForm(data)
        if form.is_valid():
            patient = form.save()
            return JsonResponse({
                "success": True,
                "patient_id": patient.id,
                "url": f"/patients/{patient.id}/",
            })
        return JsonResponse({"success": False, "errors": form.errors})
    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def profile(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, "patients/profile.html", {"patient": patient})


@login_required
def edit_profile(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        patient.blood_group = request.POST.get("blood_group", "")
        patient.genotype = request.POST.get("genotype", "")
        patient.known_conditions = request.POST.get("known_conditions", "")
        patient.save()
        messages.success(request, "Medical profile updated.")
        return redirect("patients:profile", pk=pk)
    return render(request, "patients/edit_profile.html", {"patient": patient})


@login_required
def history(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    vitals = patient.vitalsrecord_set.all().order_by("-recorded_at")

    vitals_with_indicators = []
    for i, v in enumerate(vitals):
        prev = vitals[i + 1] if i + 1 < len(vitals) else None
        vitals_with_indicators.append({
            "record": v,
            "prev": prev,
        })

    chart_data = {
        "labels": [v.recorded_at.strftime("%Y-%m-%d %H:%M") for v in vitals.order_by("recorded_at")],
        "systolic": [v.systolic for v in vitals.order_by("recorded_at") if v.systolic is not None],
        "diastolic": [v.diastolic for v in vitals.order_by("recorded_at") if v.diastolic is not None],
        "pulse": [v.pulse for v in vitals.order_by("recorded_at") if v.pulse is not None],
        "temperature": [float(v.temperature) for v in vitals.order_by("recorded_at") if v.temperature is not None],
        "glucose": [float(v.glucose_value) for v in vitals.order_by("recorded_at") if v.glucose_value is not None],
    }

    return render(request, "patients/history.html", {
        "patient": patient,
        "vitals_with_indicators": vitals_with_indicators,
        "chart_data": chart_data,
    })
