from django.db import models
from django.core.validators import RegexValidator


class Patient(models.Model):
    BLOOD_GROUPS = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ]

    GENOTYPES = [
        ("AA", "AA"), ("AS", "AS"), ("SS", "SS"),
        ("AC", "AC"), ("SC", "SC"), ("CC", "CC"),
    ]

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
    ]

    AGE_RANGE_CHOICES = [
        ("0-5", "0-5"),
        ("6-12", "6-12"),
        ("13-17", "13-17"),
        ("18-25", "18-25"),
        ("26-35", "26-35"),
        ("36-45", "36-45"),
        ("46-55", "46-55"),
        ("56-65", "56-65"),
        ("65+", "65+"),
    ]

    KNOWN_CONDITIONS = [
        ("hypertension", "Hypertension"),
        ("diabetes", "Diabetes"),
        ("asthma", "Asthma"),
        ("ulcer", "Ulcer"),
        ("allergies", "Allergies"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(regex=r"^[\+]?[\d\s\-]{7,15}$", message="Enter a valid phone number.")],
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age_range = models.CharField(max_length=5, choices=AGE_RANGE_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True, default="")
    genotype = models.CharField(max_length=3, choices=GENOTYPES, blank=True, default="")
    known_conditions = models.TextField(blank=True, default="", help_text="Comma-separated list of conditions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["last_name", "first_name"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def conditions_list(self):
        if not self.known_conditions.strip():
            return []
        return [c.strip() for c in self.known_conditions.split(",") if c.strip()]
