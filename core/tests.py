from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from .health_data_gateway import _database_is_configured, _row_cause_name
from .risk_engine import build_risk_result
from .stayfit_api import EXERCISE_POOL, RISK_ROUTINES, build_stayfit_routine, get_replacement_exercise


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_file(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


class HealthDataGatewayConfigurationTests(SimpleTestCase):
    def test_gateway_is_enabled_for_postgresql(self):
        databases = {"default": {"ENGINE": "django.db.backends.postgresql"}}
        with patch.dict(settings.DATABASES, databases, clear=True):
            self.assertTrue(_database_is_configured())

    def test_gateway_is_disabled_for_sqlite(self):
        databases = {"default": {"ENGINE": "django.db.backends.sqlite3"}}
        with patch.dict(settings.DATABASES, databases, clear=True):
            self.assertFalse(_database_is_configured())

    def test_cause_id_is_not_used_as_cause_name(self):
        cause_name = _row_cause_name(
            {"cause_id": 12},
            cause_col=None,
            cause_id_col="cause_id",
            cause_lookup={},
        )

        self.assertEqual(cause_name, "")

    @patch("core.risk_engine.fetch_mortality_match")
    def test_unknown_database_cause_falls_back_to_known_copy(self, mortality_match):
        mortality_match.return_value = type(
            "MortalityMatch",
            (),
            {
                "cause_id": 12,
                "cause_name": "12",
                "source_table": "mortality_record",
                "fallback_used": False,
            },
        )()

        result = build_risk_result(
            {"age": 48, "sex": "Male", "state": "Selangor"},
            {"habits": ["Rarely exercise"], "family_history": []},
        )

        self.assertIn(
            result["top_risk"]["name"],
            {"Heart disease", "Stroke", "Type 2 diabetes", "Cancer", "Respiratory disease"},
        )

    @patch("core.stayfit_api._database_exercise_pool")
    def test_stayfit_routine_prefers_database_exercise_pool(self, database_pool):
        database_pool.return_value = [
            {
                "id": "step_jack",
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
                "id": "wall_push_up",
                "wger_id": 2,
                "wger_uuid": None,
                "name": "Database Wall Press",
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

        self.assertEqual(routine["exercises"][0]["id"], "step_jack")
        self.assertEqual(routine["exercises"][0]["name"], "Database Step")
        self.assertEqual(routine["exercises"][2]["name"], "Database Wall Press")

    @patch("core.stayfit_api._database_exercise_pool")
    def test_stayfit_reshuffle_falls_back_only_to_matching_plan_tag(self, database_pool):
        database_pool.return_value = [
            {
                "id": "db_unrelated",
                "wger_id": 3,
                "wger_uuid": None,
                "name": "Database Unrelated",
                "category": "Other",
                "equipment": "none",
                "muscles": [],
                "sets": 1,
                "reps": 1,
                "duration_seconds": None,
                "instructions": "Unrelated.",
                "image_url": None,
                "video_url": None,
                "source_url": "https://wger.de/",
                "source_note": "Loaded from test database pool.",
                "difficulty": "beginner",
                "plan_tags": ["unrelated"],
            }
        ]

        exercise = get_replacement_exercise(
            "deep_breathing",
            plan_tag="respiratory_disease",
            risk_key="respiratory_disease",
        )

        self.assertIn("respiratory_disease", exercise["plan_tags"])
        self.assertNotEqual(exercise["id"], "db_unrelated")


class StaticAcceptanceTests(SimpleTestCase):
    def test_dashboard_exercise_action_uses_real_top_risk_slug(self):
        dashboard_js = project_file("core/static/core/js/dashboard.js")
        statistics_js = project_file("core/static/core/js/statistics.js")

        self.assertIn('target: "/stayfit/?risk=heart-disease"', dashboard_js)
        self.assertIn('/stayfit/?risk=${encodeURIComponent(stats.top.slug)}', statistics_js)
        self.assertIn("Start a Stay Fit routine", statistics_js)

    def test_navigation_labels_and_active_route_mapping(self):
        nav_html = project_file("core/static/core/components/nav.html")
        include_js = project_file("core/static/core/js/include.js")

        for label in ["My Plan", "Stay Fit", "Data Sources"]:
            self.assertIn(label, nav_html)
        self.assertNotIn("Find Specialist", nav_html)
        self.assertIn('data-nav-section="plan"', nav_html)
        self.assertIn('data-nav-section="sources"', nav_html)
        self.assertIn('"/dashboard/"', include_js)
        self.assertIn('"/readmore/"', include_js)
        self.assertIn('if (path === "/source/") return "sources";', include_js)

    def test_stayfit_static_hooks_cover_timer_guideline_and_modal_video_loop(self):
        stayfit_html = project_file("core/templates/core/stayfit.html")
        stayfit_js = project_file("core/static/core/js/stayfit.js")
        stayfit_css = project_file("core/static/core/css/style.css")

        for hook in [
            'id="timer-display"',
            'id="timer-toggle"',
            'id="timer-reset"',
            'id="timer-add-minute"',
            'id="guideline-note"',
            'id="exercise-modal-media"',
            'id="intensity-options"',
        ]:
            self.assertIn(hook, stayfit_html)
        for video_flag in ["video.loop = true", "video.autoplay = true", "video.muted = true", "video.playsInline = true"]:
            self.assertIn(video_flag, stayfit_js)
        self.assertIn("renderGuidelineNote", stayfit_js)
        self.assertIn("renderIntensityOptions", stayfit_js)
        self.assertIn("renderExerciseIllustration", stayfit_js)
        self.assertIn("const TIMER_MIN_SECONDS = 60;", stayfit_js)
        self.assertIn("Math.min(max, Math.max(min, number))", stayfit_js)
        self.assertIn("background: var(--green-strong);", stayfit_css)
        self.assertNotIn("conic-gradient(var(--green-strong)", stayfit_css)

    def test_stayfit_exercise_order_is_user_directed_without_list_modal(self):
        stayfit_js = project_file("core/static/core/js/stayfit.js")

        self.assertNotIn("showGuidanceExercise(stayfitState.activeExerciseIndex + 1)", stayfit_js)
        self.assertNotIn("startExerciseCarousel();", stayfit_js)
        self.assertIn("stayfitState.remainingSeconds = stayfitState.totalSeconds;", stayfit_js)

        list_click_block = (
            'detailButton.addEventListener("click", () => {\n'
            "      showGuidanceExercise(index);\n"
            "    });"
        )
        self.assertIn(list_click_block, stayfit_js)
        self.assertIn('panel.addEventListener("click", openCurrentGuidanceExercise)', stayfit_js)


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
        self.assertContains(dashboard_response, 'data-include="footer"')
        self.assertContains(dashboard_response, "What to do next")
        self.assertContains(dashboard_response, "Connected database", count=0)

        footer_html = project_file("core/static/core/components/footer.html")
        self.assertIn("This is not a diagnosis", footer_html)

    def test_readmore_page_is_public(self):
        response = self.client.get(reverse("readmore"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Heart disease")
        self.assertContains(response, "Where this comes from")

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
        self.assertEqual(data["level_label"], "Low")
        self.assertEqual(len(data["exercises"]), 4)
        self.assertEqual(data["exercises"][0]["id"], "step_jack")
        self.assertEqual(len(data["risk_options"]), 5)
        self.assertEqual(len(data["level_options"]), 3)
        self.assertEqual(data["guideline"]["name"], "Garis Panduan Aktiviti Fizikal Malaysia")
        self.assertIn("infosihat.moh.gov.my", data["guideline"]["url"])
        self.assertIn("guidance_tip", data)
        self.assertIn("wger", data["source"]["usage"])

    def test_stayfit_routine_api_scales_intensity_levels(self):
        low = self.client.get(
            reverse("api_stayfit_routine"),
            {"risk": "type_2_diabetes", "level": "beginner"},
        ).json()
        medium = self.client.get(
            reverse("api_stayfit_routine"),
            {"risk": "type_2_diabetes", "level": "standard"},
        ).json()
        high = self.client.get(
            reverse("api_stayfit_routine"),
            {"risk": "type_2_diabetes", "level": "progress"},
        ).json()

        self.assertEqual([low["level_label"], medium["level_label"], high["level_label"]], ["Low", "Medium", "High"])
        self.assertLess(low["duration_minutes"], medium["duration_minutes"])
        self.assertLess(medium["duration_minutes"], high["duration_minutes"])
        self.assertLess(low["exercises"][0]["reps"], medium["exercises"][0]["reps"])
        self.assertLess(medium["exercises"][0]["reps"], high["exercises"][0]["reps"])

    def test_stayfit_routine_api_keeps_four_exercises_for_every_focus(self):
        risks = [
            "heart_disease",
            "stroke",
            "type_2_diabetes",
            "respiratory_disease",
            "cancer",
            "lung-cancer",
        ]

        for risk in risks:
            with self.subTest(risk=risk):
                response = self.client.get(reverse("api_stayfit_routine"), {"risk": risk})
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(len(data["exercises"]), 4)
                self.assertGreaterEqual(data["duration_minutes"], 1)

    def test_stayfit_fallback_pool_has_at_least_ten_movements_per_focus(self):
        for risk_key, routine in RISK_ROUTINES.items():
            with self.subTest(risk=risk_key):
                count = sum(
                    1
                    for exercise in EXERCISE_POOL
                    if routine["plan_tag"] in exercise["plan_tags"]
                )
                self.assertGreaterEqual(count, 10)

    def test_stayfit_routine_api_returns_selected_risk_routine(self):
        response = self.client.get(reverse("api_stayfit_routine"), {"risk": "respiratory_disease"})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["selected_risk"]["label"], "Respiratory disease")
        self.assertEqual(data["plan_tag"], "respiratory_disease")
        self.assertEqual(data["exercises"][0]["id"], "deep_breathing")
        self.assertEqual(data["exercises"][1]["id"], "shoulder_roll")

    def test_stayfit_reshuffle_api_replaces_current_exercise(self):
        response = self.client.get(
            reverse("api_stayfit_reshuffle"),
            {"current": "deep_breathing", "risk": "respiratory_disease"},
        )

        self.assertEqual(response.status_code, 200)
        exercise = response.json()["exercise"]
        self.assertNotEqual(exercise["id"], "deep_breathing")
        self.assertIn("respiratory_disease", exercise["plan_tags"])
        self.assertIn("instructions", exercise)

    def test_stayfit_reshuffle_moves_forward_through_matching_pool(self):
        first = get_replacement_exercise("deep_breathing", risk_key="respiratory_disease")
        second = get_replacement_exercise(first["id"], risk_key="respiratory_disease")

        self.assertNotEqual(first["id"], second["id"])
        self.assertIn("respiratory_disease", first["plan_tags"])
        self.assertIn("respiratory_disease", second["plan_tags"])

    def test_source_page_contains_specialist_anchor_for_navigation(self):
        response = self.client.get(reverse("source"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="specialist"')
