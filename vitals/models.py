from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from patients.models import Patient
from accounts.models import User


class VitalsRecord(models.Model):
    GLUCOSE_TYPES = [
        ("FBS", "Fasting (FBS)"),
        ("RBS", "Random (RBS)"),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="vitalsrecord_set")
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    systolic = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(60), MaxValueValidator(250)],
        help_text="Normal: 90-120 mmHg"
    )
    diastolic = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(40), MaxValueValidator(180)],
        help_text="Normal: 60-80 mmHg"
    )
    pulse = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(30), MaxValueValidator(220)],
        help_text="Normal: 60-100 bpm"
    )
    temperature = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True, blank=True,
        validators=[MinValueValidator(30.0), MaxValueValidator(45.0)],
        help_text="Normal: 36.1-37.2 C"
    )
    glucose_type = models.CharField(max_length=3, choices=GLUCOSE_TYPES, default="RBS", blank=True)
    glucose_value = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True, blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(40.0)],
        help_text="Normal FBS: 3.9-5.5, RBS: <7.8 mmol/L"
    )
    notes = models.TextField(blank=True, default="")
    medications = models.TextField(blank=True, default="")

    correction_requested = models.BooleanField(default=False)
    correction_reason = models.TextField(blank=True, default="")
    correction_approved = models.BooleanField(default=False)

    recorded_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["patient", "-recorded_at"]),
        ]

    def __str__(self):
        return f"{self.patient.full_name} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_editable(self):
        if self.correction_requested and not self.correction_approved:
            return False
        return (timezone.now() - self.created_at).total_seconds() <= 300

    @property
    def is_critical(self):
        return (
            (self.systolic is not None and self.systolic >= 140)
            or (self.diastolic is not None and self.diastolic >= 90)
            or (self.pulse is not None and (self.pulse > 120 or self.pulse < 60))
            or (self.temperature is not None and (self.temperature > 38.0 or self.temperature < 36.1))
            or (self.glucose_value is not None and self.glucose_type == "FBS" and self.glucose_value >= 7.0)
            or (self.glucose_value is not None and self.glucose_type == "RBS" and self.glucose_value > 11.0)
        )

    @property
    def is_elevated(self):
        if self.is_critical:
            return False
        return (
            (self.systolic is not None and 120 <= self.systolic <= 139)
            or (self.diastolic is not None and 80 <= self.diastolic <= 89)
            or (self.pulse is not None and 100 <= self.pulse <= 120)
            or (self.temperature is not None and 37.3 <= self.temperature <= 38.0)
            or (self.glucose_value is not None and self.glucose_type == "FBS" and 5.6 <= self.glucose_value < 7.0)
            or (self.glucose_value is not None and self.glucose_type == "RBS" and 7.8 <= self.glucose_value <= 11.0)
        )
