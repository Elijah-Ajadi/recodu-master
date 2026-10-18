from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class VolunteerPasswordResetTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="superadmin",
            email="admin@example.com",
            password="Original-admin-pass-123!",
        )
        self.volunteer = User.objects.create_user(
            username="volunteer",
            password="Original-volunteer-pass-123!",
            role="VOLUNTEER",
        )
        self.url = reverse(
            "dashboard:reset_volunteer_password",
            kwargs={"pk": self.volunteer.pk},
        )

    def test_superuser_can_reset_volunteer_password(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            self.url,
            {
                "new_password1": "New-volunteer-pass-456!",
                "new_password2": "New-volunteer-pass-456!",
            },
        )

        self.assertRedirects(response, reverse("dashboard:users"))
        self.volunteer.refresh_from_db()
        self.assertTrue(self.volunteer.check_password("New-volunteer-pass-456!"))
        self.assertFalse(self.volunteer.check_password("Original-volunteer-pass-123!"))

    def test_non_superuser_cannot_reset_volunteer_password(self):
        unit_head = User.objects.create_user(
            username="unithead",
            password="Unit-head-pass-123!",
            role="UNIT_HEAD",
        )
        self.client.force_login(unit_head)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_superuser_cannot_use_reset_view_for_unit_head(self):
        unit_head = User.objects.create_user(
            username="another-unithead",
            password="Unit-head-pass-123!",
            role="UNIT_HEAD",
        )
        self.client.force_login(self.admin)

        response = self.client.get(
            reverse(
                "dashboard:reset_volunteer_password",
                kwargs={"pk": unit_head.pk},
            )
        )

        self.assertEqual(response.status_code, 404)
