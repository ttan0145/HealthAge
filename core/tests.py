from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .health_data_gateway import _database_is_configured
from .stayfit_api import build_stayfit_routine


class HealthDataGatewayConfigurationTests(SimpleTestCase):
    def test_gateway_is_enabled_for_postgresql(self):
        databases = {"default": {"ENGINE": "django.db.backends.postgresql"}}
        with patch.dict(settings.DATABASES, databases, clear=True):
            self.assertTrue(_database_is_configured())

    def test_gateway_is_disabled_for_sqlite(self):
        databases = {"default": {"ENGINE": "django.db.backends.sqlite3"}}
        with patch.dict(settings.DATABASES, databases, clear=True):
            self.assertFalse(_database_is_configured())

    @patch("core.stayfit_api._database_exercise_pool")
    def test_stayfit_routine_prefers_database_exercise_pool(self, database_pool):
        database_pool.return_value = [
            {
                "id": "db_step",
                "wger_id": 1,
                "wger_uuid": None,
                "name": "Database Step",
                "category": "Cardio",
                "equipment": "none",
                "muscles": ["Quads"],
                "sets": 1,
                "reps": 8,
                "duration_seconds": None,
                "instructions": "Step in place.",
                "image_url": None,
                "video_url": None,
                "source_url": "https://wger.de/",
                "source_note": "Loaded from test database pool.",
                "difficulty": "beginner",
                "plan_tags": ["cardio_core"],
            },
            {
                "id": "db_breath",
                "wger_id": 2,
                "wger_uuid": None,
                "name": "Database Breath",
                "category": "Chest",
                "equipment": "none",
                "muscles": ["Chest"],
                "sets": 1,
                "reps": None,
                "duration_seconds": 30,
                "instructions": "Breathe slowly.",
                "image_url": None,
                "video_url": None,
                "source_url": "https://wger.de/",
                "source_note": "Loaded from test database pool.",
                "difficulty": "beginner",
                "plan_tags": ["cardio_core"],
            },
        ]

        routine = build_stayfit_routine()

        self.assertEqual(routine["exercises"][0]["id"], "db_step")
        self.assertEqual(routine["exercises"][1]["name"], "Database Breath")


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

    def test_stayfit_page_loads_dynamic_hooks(self):
        response = self.client.get(reverse("stayfit"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="exercise-list"')
        self.assertContains(response, 'id="risk-options"')
        self.assertContains(response, "/static/core/js/stayfit.js")

    def test_stayfit_routine_api_returns_mr_lim_contract(self):
        response = self.client.get(reverse("api_stayfit_routine"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["persona"]["name"], "Mr Lim Wei Jian")
        self.assertEqual(data["selected_risk"]["key"], "heart_disease")
        self.assertEqual(data["title"], "Heart disease: low-impact cardio and core")
        self.assertEqual(len(data["exercises"]), 4)
        self.assertEqual(data["exercises"][0]["id"], "step_jack")
        self.assertEqual(len(data["risk_options"]), 5)
        self.assertIn("guidance_tip", data)
        self.assertIn("wger", data["source"]["usage"])

    def test_stayfit_routine_api_returns_selected_risk_routine(self):
        response = self.client.get(reverse("api_stayfit_routine"), {"risk": "respiratory_disease"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["selected_risk"]["label"], "Respiratory disease")
        self.assertEqual(data["plan_tag"], "respiratory_disease")
        self.assertEqual(data["exercises"][0]["id"], "deep_breathing")
        self.assertEqual(data["exercises"][1]["id"], "torso_rotation")

    def test_stayfit_reshuffle_api_replaces_current_exercise(self):
        response = self.client.get(
            reverse("api_stayfit_reshuffle"),
            {"current": "deep_breathing", "risk": "respiratory_disease"},
        )

        self.assertEqual(response.status_code, 200)
        exercise = response.json()["exercise"]
        self.assertNotEqual(exercise["id"], "deep_breathing")
        self.assertIn("instructions", exercise)
