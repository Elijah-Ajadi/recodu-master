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
        self.assertContains(response, f"#vitals-{self.vital.id}")

    def test_create_patient_api_success(self):
        url = reverse("patients:create")
        payload = {
            "first_name": "Ademola",
            "last_name": "Ajadi",
            "phone": "",
            "date_of_birth": "",
            "home_address": "",
            "gender": "",
            "age_range": "",
        }
        response = self.client.post(
            url,
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        new_patient = Patient.objects.get(id=data["patient_id"])
        self.assertEqual(new_patient.first_name, "Ademola")
        self.assertEqual(new_patient.last_name, "Ajadi")

    def test_create_patient_api_validation_error(self):
        url = reverse("patients:create")
        payload = {
            "first_name": "",
            "last_name": "Ajadi",
        }
        response = self.client.post(
            url,
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data["success"])
        self.assertIn("first_name", data["errors"])

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

    def test_create_patient_api_leap_year_dob(self):
        url = reverse("patients:create")
        payload = {
            "first_name": "Kofi",
            "last_name": "Annan",
            "date_of_birth": "2000-02-29",
        }
        response = self.client.post(
            url,
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        new_patient = Patient.objects.get(id=data["patient_id"])
        self.assertIsNotNone(new_patient.days_to_birthday)

        # Check profile page renders without error
        profile_response = self.client.get(reverse("patients:profile", kwargs={"pk": new_patient.id}))
        self.assertEqual(profile_response.status_code, 200)

    def test_create_patient_api_unauthenticated_redirects(self):
        self.client.logout()
        url = reverse("patients:create")
        payload = {"first_name": "Unauth"}
        response = self.client.post(
            url,
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_create_patient_api_form_encoded(self):
        url = reverse("patients:create")
        response = self.client.post(
            url,
            data={"first_name": "FormUser", "last_name": "Test"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
