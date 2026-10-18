import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from patients.models import Patient

User = get_user_model()


class NameOnlyPatientRegistrationTests(TestCase):
    def setUp(self):
        self.volunteer = User.objects.create_user(
            username="intake-volunteer",
            password="Volunteer-pass-123!",
            role="VOLUNTEER",
        )
        self.client.force_login(self.volunteer)
        self.url = reverse("patients:create")

    def test_first_name_alone_creates_patient_profile(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"first_name": "Amaka"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["success"])

        patient = Patient.objects.get(pk=payload["patient_id"])
        self.assertEqual(patient.first_name, "Amaka")
        self.assertEqual(patient.last_name, "")
        self.assertIsNone(patient.phone)
        self.assertIsNone(patient.date_of_birth)
        self.assertEqual(patient.gender, "")
        self.assertEqual(patient.home_address, "")

    def test_missing_name_does_not_create_patient(self):
        response = self.client.post(
            self.url,
            data=json.dumps({"last_name": "Okafor"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertEqual(Patient.objects.count(), 0)

    def test_malformed_json_returns_client_error(self):
        response = self.client.post(
            self.url,
            data="{invalid",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
