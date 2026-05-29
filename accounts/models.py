from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ("UNIT_HEAD", "Unit Head"),
        ("VOLUNTEER", "Volunteer"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="VOLUNTEER")

    def is_unit_head(self):
        return self.role == "UNIT_HEAD" or self.is_superuser

    def is_volunteer(self):
        return self.role == "VOLUNTEER"
