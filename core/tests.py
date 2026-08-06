from django.test import TestCase
from django.urls import reverse


class HealthAgeFlowTests(TestCase):
    def test_profile_rejects_invalid_age(self):
        response = self.client.post(
            reverse("profile"),
            {
                "full_name": "Lim Wei Jian",
                "age": "120",
                "sex": "Male",
                "state": "Selangor",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Age must be between 18 and 100.")

    def test_profile_and_lifestyle_create_dashboard_result(self):
        profile_response = self.client.post(
            reverse("profile"),
            {
                "full_name": "Lim Wei Jian",
                "age": "48",
                "sex": "Male",
                "state": "Selangor",
            },
        )
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
