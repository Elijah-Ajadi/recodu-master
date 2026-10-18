from django.contrib import admin
from .models import VitalsRecord


@admin.register(VitalsRecord)
class VitalsRecordAdmin(admin.ModelAdmin):
    list_display = ("patient", "recorded_by", "systolic", "diastolic", "pulse", "temperature", "glucose_type", "glucose_value", "recorded_at")
    list_filter = ("glucose_type", "correction_requested", "recorded_at")
    search_fields = ("patient__first_name", "patient__last_name")
    date_hierarchy = "recorded_at"
