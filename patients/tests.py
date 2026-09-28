from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from patients.models import Patient
from vitals.models import VitalsRecord


class PatientViewsTest(TestCase):
    def setUp(self):
        self.volunteer = User.objects.create_user(
            username="volunteer1",
            password="password123",
            role="VOLUNTEER",
        )
        self.client = Client()
        self.client.login(username="volunteer1", password="password123")

        self.patient = Patient.objects.create(
            first_name="Chioma",
            last_name="Adeyemi",
            phone="+2348033334444",
            gender="F",
        )

        self.vital = VitalsRecord.objects.create(
            patient=self.patient,
            recorded_by=self.volunteer,
            systolic=120,
            diastolic=80,
            pulse=72,
            temperature=36.6,
            glucose_type="RBS",
            glucose_value=5.4,
        )

    def test_search_view_contains_recent_intakes(self):
        response = self.client.get(reverse("patients:search"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("recent_intakes", response.context)
        self.assertEqual(len(response.context["recent_intakes"]), 1)
        self.assertContains(response, "Chioma Adeyemi")
        self.assertContains(response, "120/80")
        self.assertContains(response, f"#vitals-{self.vital.id}")

    def test_edit_profile_updates_demographics(self):
        response = self.client.post(
            reverse("patients:edit_profile", kwargs={"pk": self.patient.id}),
            {
                "first_name": "Chioma",
                "last_name": "Adeyemi-Okoro",
                "phone": "+2348033334444",
                "gender": "F",
                "blood_group": "O+",
                "genotype": "AA",
                "home_address": "15 Health Boulevard",
                "known_conditions": "hypertension",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.last_name, "Adeyemi-Okoro")
        self.assertEqual(self.patient.blood_group, "O+")
        self.assertEqual(self.patient.genotype, "AA")
        self.assertEqual(self.patient.home_address, "15 Health Boulevard")
