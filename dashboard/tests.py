import io
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from patients.models import Patient


class ImportPatientsTest(TestCase):
    def setUp(self):
        self.unit_head = User.objects.create_user(
            username="unithead",
            password="password123",
            role="UNIT_HEAD",
        )
        self.client = Client()
        self.client.login(username="unithead", password="password123")

    def test_import_with_only_name(self):
        csv_content = "first_name,last_name\nNgozi,Eze\nEmeka,\n"
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "patients.csv"

        response = self.client.post(
            reverse("dashboard:import_patients"),
            {"csv_file": csv_file},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Patient.objects.filter(first_name="Ngozi", last_name="Eze").exists())
        self.assertTrue(Patient.objects.filter(first_name="Emeka", last_name="").exists())
        self.assertEqual(Patient.objects.count(), 2)

    def test_import_with_full_name_column(self):
        csv_content = "name,phone\nTunde Bakare,+2348098765432\nBolanle Alabi,\n"
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "patients.csv"

        response = self.client.post(
            reverse("dashboard:import_patients"),
            {"csv_file": csv_file},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        tunde = Patient.objects.get(first_name="Tunde")
        self.assertEqual(tunde.last_name, "Bakare")
        self.assertEqual(tunde.phone, "+2348098765432")

        bolanle = Patient.objects.get(first_name="Bolanle")
        self.assertEqual(bolanle.last_name, "Alabi")
        self.assertIsNone(bolanle.phone)

    def test_multiple_patients_without_phone_do_not_conflict(self):
        csv_content = "first_name,last_name\nPatient1,One\nPatient2,Two\nPatient3,Three\n"
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "patients.csv"

        response = self.client.post(
            reverse("dashboard:import_patients"),
            {"csv_file": csv_file},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Patient.objects.count(), 3)

    def test_import_with_empty_phone_field_in_csv(self):
        csv_content = "name,phone,gender\nMama Adetunji Abigail,,F\n"
        csv_file = io.BytesIO(csv_content.encode("utf-8"))
        csv_file.name = "patients.csv"

        response = self.client.post(
            reverse("dashboard:import_patients"),
            {"csv_file": csv_file},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        patient = Patient.objects.get(first_name="Mama")
        self.assertIsNone(patient.phone)
