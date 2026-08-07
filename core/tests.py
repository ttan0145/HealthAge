from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .health_data_gateway import _database_is_configured


class HealthDataGatewayConfigurationTests(SimpleTestCase):
    def test_gateway_is_enabled_for_postgresql(self):
        databases = {"default": {"ENGINE": "django.db.backends.postgresql"}}
        with patch.dict(settings.DATABASES, databases, clear=True):
            self.assertTrue(_database_is_configured())

    def test_gateway_is_disabled_for_sqlite(self):
        databases = {"default": {"ENGINE": "django.db.backends.sqlite3"}}
        with patch.dict(settings.DATABASES, databases, clear=True):
            self.assertFalse(_database_is_configured())


class HealthAgeFlowTests(TestCase):
    valid_profile = {
        "age": "48",
        "sex": "Male",
        "state": "Selangor",
    }

    def test_profile_intake_collects_only_required_demographics(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="age"')
        self.assertContains(response, 'name="sex"')
        self.assertContains(response, 'name="state"')
        self.assertNotContains(response, 'name="full_name"')

    def test_profile_rejects_invalid_age(self):
        response = self.client.post(
            reverse("profile"),
            {
                "age": "120",
                "sex": "Male",
                "state": "Selangor",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Age must be between 18 and 100.")

    def test_profile_rejects_missing_or_unknown_values(self):
        invalid_profiles = [
            ({**self.valid_profile, "age": ""}, "Enter an age as a number."),
            ({**self.valid_profile, "sex": "Unknown"}, "Choose a valid sex."),
            (
                {**self.valid_profile, "state": "Unknown"},
                "Choose a valid Malaysian state.",
            ),
        ]

        for profile, error in invalid_profiles:
            with self.subTest(profile=profile):
                response = self.client.post(reverse("profile"), profile)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, error)

    def test_profile_session_excludes_name(self):
        response = self.client.post(reverse("profile"), self.valid_profile)

        self.assertRedirects(response, reverse("lifestyle"))
        self.assertNotIn("name", self.client.session["profile"])

    def test_lifestyle_requires_one_or_two_known_habits(self):
        self.client.post(reverse("profile"), self.valid_profile)

        missing_response = self.client.post(reverse("lifestyle"), {"habits": []})
        self.assertEqual(missing_response.status_code, 200)
        self.assertContains(missing_response, "Choose one or two habits")

        excessive_response = self.client.post(
            reverse("lifestyle"),
            {"habits": ["Smoking", "Rarely exercise", "Sleep late"]},
        )
        self.assertEqual(excessive_response.status_code, 200)
        self.assertContains(excessive_response, "Choose no more than two habits.")

        unknown_response = self.client.post(
            reverse("lifestyle"),
            {"habits": ["Unknown habit"]},
        )
        self.assertEqual(unknown_response.status_code, 200)
        self.assertContains(unknown_response, "Choose habits from the available options.")

    def test_profile_and_lifestyle_create_dashboard_result(self):
        profile_response = self.client.post(reverse("profile"), self.valid_profile)
        self.assertRedirects(profile_response, reverse("lifestyle"))

        lifestyle_response = self.client.post(
            reverse("lifestyle"),
            {
                "habits": ["Rarely exercise", "High work stress"],
                "family_history": ["Heart disease"],
            },
        )
        self.assertRedirects(lifestyle_response, reverse("dashboard"))

        dashboard_response = self.client.get(reverse("dashboard"))
        self.assertContains(dashboard_response, "This is not a diagnosis.")
        self.assertContains(dashboard_response, "What to do next")
        self.assertContains(dashboard_response, "Connected database", count=0)

    def test_readmore_requires_a_result(self):
        response = self.client.get(reverse("readmore"))

        self.assertRedirects(response, reverse("profile"))

    def test_source_page_is_public(self):
        response = self.client.get(reverse("source"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sources used by HealthAge")
