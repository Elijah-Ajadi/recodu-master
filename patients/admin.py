from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "gender", "age_range", "blood_group")
    list_filter = ("gender", "age_range", "blood_group", "genotype")
    search_fields = ("first_name", "last_name", "phone")
