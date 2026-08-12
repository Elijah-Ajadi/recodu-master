import csv
import io
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


# ---------------------------------------------------------------------------
# CSV Template download
# ---------------------------------------------------------------------------

IMPORT_CSV_COLUMNS = [
    "first_name", "last_name", "phone", "gender",
    "date_of_birth", "age_range", "blood_group", "genotype",
    "known_conditions", "home_address",
]

IMPORT_CSV_SAMPLE = [
    "Ada", "Okonkwo", "+2348012345678", "F",
    "1985-04-12", "36-45", "O+", "AA",
    "hypertension,diabetes", "12 Murtala Way, Lagos",
]


@login_required
@user_passes_test(is_unit_head)
def download_template(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="recodu_import_template.csv"'
    writer = csv.writer(response)
    writer.writerow(IMPORT_CSV_COLUMNS)
    writer.writerow(IMPORT_CSV_SAMPLE)
    return response


# ---------------------------------------------------------------------------
# Patient mass import
# ---------------------------------------------------------------------------

VALID_GENDERS = {"M", "F"}
VALID_AGE_RANGES = {"0-5", "6-12", "13-17", "18-25", "26-35", "36-45", "46-55", "56-65", "65+"}
VALID_BLOOD_GROUPS = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
VALID_GENOTYPES = {"AA", "AS", "SS", "AC", "SC", "CC"}


def _validate_import_row(row_dict, row_num, seen_phones):
    """
    Validate a single CSV row dict.
    Returns (patient_instance_or_None, list_of_error_strings).
    """
    errors = []

    first_name = row_dict.get("first_name", "").strip()
    last_name = row_dict.get("last_name", "").strip()
    phone = row_dict.get("phone", "").strip()
    gender = row_dict.get("gender", "").strip().upper()
    date_of_birth = row_dict.get("date_of_birth", "").strip() or None
    age_range = row_dict.get("age_range", "").strip()
    blood_group = row_dict.get("blood_group", "").strip()
    genotype = row_dict.get("genotype", "").strip()
    known_conditions = row_dict.get("known_conditions", "").strip()
    home_address = row_dict.get("home_address", "").strip()

    # Required fields
    if not first_name:
        errors.append("first_name is required")
    if not last_name:
        errors.append("last_name is required")
    if not phone:
        errors.append("phone is required")
    if not gender:
        errors.append("gender is required")

    # Choice validation (only if value is provided)
    if gender and gender not in VALID_GENDERS:
        errors.append(f"gender must be M or F (got '{gender}')")
    if age_range and age_range not in VALID_AGE_RANGES:
        errors.append(f"age_range '{age_range}' is not a valid choice")
    if blood_group and blood_group not in VALID_BLOOD_GROUPS:
        errors.append(f"blood_group '{blood_group}' is not a valid choice")
    if genotype and genotype not in VALID_GENOTYPES:
        errors.append(f"genotype '{genotype}' is not a valid choice")

    # Phone format (basic: digits, spaces, dashes, optional leading +, 7-15 chars)
    import re
    if phone and not re.match(r"^[\+]?[\d\s\-]{7,15}$", phone):
        errors.append(f"phone '{phone}' is not a valid phone number")

    # Duplicate within this file
    if phone and phone in seen_phones:
        errors.append(f"phone '{phone}' appears more than once in this file")
    elif phone:
        seen_phones.add(phone)

    # Duplicate in database
    if phone and not errors:
        if Patient.objects.filter(phone=phone).exists():
            errors.append(f"phone '{phone}' is already registered in the system")

    if errors:
        return None, errors

    # Build the Patient instance (don't save yet)
    patient = Patient(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        gender=gender,
        age_range=age_range,
        blood_group=blood_group,
        genotype=genotype,
        known_conditions=known_conditions,
        home_address=home_address,
    )

    # date_of_birth — try to parse, soft-fail
    if date_of_birth:
        from datetime import date as date_type
        try:
            from datetime import datetime
            patient.date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"date_of_birth '{date_of_birth}' must be in YYYY-MM-DD format")
            return None, errors

    return patient, []


@login_required
@user_passes_test(is_unit_head)
def import_patients(request):
    context = {}

    if request.method == "POST":
        uploaded_file = request.FILES.get("csv_file")

        if not uploaded_file:
            messages.error(request, "Please select a CSV file to upload.")
            return render(request, "dashboard/import.html", context)

        if not uploaded_file.name.endswith(".csv"):
            messages.error(request, "Only .csv files are accepted.")
            return render(request, "dashboard/import.html", context)

        # Decode the uploaded bytes
        try:
            file_content = uploaded_file.read().decode("utf-8-sig")  # utf-8-sig handles Excel BOM
        except UnicodeDecodeError:
            messages.error(request, "Could not read the file. Ensure it is saved as UTF-8 CSV.")
            return render(request, "dashboard/import.html", context)

        reader = csv.DictReader(io.StringIO(file_content))

        # Validate expected columns
        required_columns = {"first_name", "last_name", "phone", "gender"}
        if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
            missing = required_columns - set(reader.fieldnames or [])
            messages.error(request, f"CSV is missing required column(s): {', '.join(sorted(missing))}. Please use the provided template.")
            return render(request, "dashboard/import.html", context)

        valid_patients = []
        failed_rows = []
        seen_phones = set()

        for row_num, row in enumerate(reader, start=2):  # row 1 = header
            patient, errors = _validate_import_row(row, row_num, seen_phones)
            if patient:
                valid_patients.append(patient)
            else:
                failed_rows.append({
                    "row": row_num,
                    "name": f"{row.get('first_name', '').strip()} {row.get('last_name', '').strip()}".strip() or "—",
                    "phone": row.get("phone", "").strip() or "—",
                    "errors": errors,
                })

        # Bulk create all valid patients
        if valid_patients:
            # bulk_create doesn't call save(), so auto age_range logic won't run.
            # Call full save() individually for patients that have date_of_birth.
            needs_save = [p for p in valid_patients if p.date_of_birth and not p.age_range]
            bulk_only = [p for p in valid_patients if p not in needs_save]

            Patient.objects.bulk_create(bulk_only)
            for p in needs_save:
                p.save()  # triggers age_range auto-set in Patient.save()

        context["imported_count"] = len(valid_patients)
        context["failed_rows"] = failed_rows
        context["show_results"] = True

    return render(request, "dashboard/import.html", context)

