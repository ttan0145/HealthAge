"""Stay Fit routine data contract for the MVP.

This module deliberately returns a small curated routine instead of proxying
wger live during the user flow. The exercise facts are wger-sourced where
available; the prescription fields such as sets, reps, duration and tips are
HealthAge MVP logic.
"""

from __future__ import annotations

from copy import deepcopy
import json
from typing import Any

from django.conf import settings
from django.db import DatabaseError, connection


MR_LIM_PERSONA = {
    "name": "Mr Lim Wei Jian",
    "age": 48,
    "occupation": "Operations Manager",
    "location": "Urban Malaysia",
    "habits": [
        "rarely exercises",
        "eats irregularly",
        "sleeps late",
        "no recent screening",
    ],
    "goal": "Build healthier habits gradually without feeling overwhelmed.",
}


EXERCISE_POOL = [
    {
        "id": "step_jack",
        "wger_id": 1962,
        "wger_uuid": "2f10d91f-6c12-471b-bb9e-80840a56ce01",
        "name": "Step Jack",
        "category": "Cardio",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Quads", "Abs", "Glutes", "Shoulders"],
        "sets": 3,
        "reps": 15,
        "duration_seconds": None,
        "instructions": (
            "Stand upright with your feet together. Step one foot to the side "
            "while raising both arms, return to the centre, then alternate sides "
            "at a steady pace."
        ),
        "image_url": "https://wger.de/media/exercise-images/1962/74041371-1019-4f89-9ebe-cec792484a46.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1962/",
        "source_note": "Exercise name, category, muscles, equipment and image are sourced from wger.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "mobility"],
    },
    {
        "id": "bird_dog",
        "wger_id": 1572,
        "wger_uuid": None,
        "name": "Bird Dog",
        "category": "Abs",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Abs", "Glutes", "Shoulders"],
        "sets": 3,
        "reps": 10,
        "duration_seconds": None,
        "instructions": (
            "Begin on all fours with hands under shoulders and knees under hips. "
            "Extend one arm and the opposite leg, pause briefly, then return and "
            "switch sides."
        ),
        "image_url": "https://wger.de/media/exercise-images/1572/3d14e761-a73d-49da-8804-f3016a7573ff.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1572/",
        "source_note": "Exercise name, category, equipment, image and base instructions are sourced from wger.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "strength"],
    },
    {
        "id": "wall_push_up",
        "wger_id": 1551,
        "wger_uuid": None,
        "name": "Wall Push-up",
        "category": "Chest",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Chest", "Shoulders", "Triceps"],
        "sets": 3,
        "reps": 12,
        "duration_seconds": None,
        "instructions": (
            "Stand facing a wall with hands at chest height. Bend your elbows "
            "gently to bring your body closer to the wall, then push back to the "
            "start position."
        ),
        "image_url": "https://wger.de/media/exercise-images/1551/a6a9e561-3965-45c6-9f2b-ee671e1a3a45.png",
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1551/",
        "source_note": "Adapted as a low-impact variation of the wger Push-Up entry for the MVP routine.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "strength"],
    },
    {
        "id": "side_plank_knee",
        "wger_id": 580,
        "wger_uuid": None,
        "name": "Side Plank from Knees",
        "category": "Abs",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Abs", "Obliques"],
        "sets": 3,
        "reps": None,
        "duration_seconds": 20,
        "instructions": (
            "Lie on your side and support your body with your forearm and knees. "
            "Keep your hips lifted and hold a steady, comfortable position."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/580/",
        "source_note": "Adapted from the wger Side Plank entry with a beginner knee-supported variation.",
        "difficulty": "beginner",
        "plan_tags": ["cardio_core", "strength"],
    },
    {
        "id": "deep_breathing",
        "wger_id": 1591,
        "wger_uuid": None,
        "name": "Deep Breathing",
        "category": "Chest",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Chest"],
        "sets": 2,
        "reps": None,
        "duration_seconds": 45,
        "instructions": (
            "Sit or stand tall. Breathe in slowly through your nose, let your "
            "chest and belly expand, then breathe out steadily."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1591/",
        "source_note": "Exercise name and base concept are sourced from wger.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "cardio_core"],
    },
    {
        "id": "torso_rotation",
        "wger_id": 1451,
        "wger_uuid": None,
        "name": "Torso Rotation Stretch",
        "category": "Chest",
        "equipment": "none (bodyweight exercise)",
        "muscles": ["Abs", "Back"],
        "sets": 2,
        "reps": 8,
        "duration_seconds": None,
        "instructions": (
            "Stand or sit upright. Rotate your torso slowly to one side, hold "
            "briefly, then return to centre and repeat on the other side."
        ),
        "image_url": None,
        "video_url": None,
        "source_url": "https://wger.de/api/v2/exerciseinfo/1451/",
        "source_note": "Exercise name and base instructions are sourced from wger.",
        "difficulty": "beginner",
        "plan_tags": ["mobility", "cardio_core"],
    },
]


DEFAULT_ROUTINE_IDS = ["step_jack", "wall_push_up", "bird_dog", "side_plank_knee"]


def build_stayfit_routine(level: str = "beginner") -> dict[str, Any]:
    """Return the stable JSON contract consumed by the Stay Fit frontend."""
    exercise_pool = _load_exercise_pool()
    exercise_lookup = {exercise["id"]: exercise for exercise in exercise_pool}
    exercises = [
        deepcopy(exercise_lookup[exercise_id])
        for exercise_id in DEFAULT_ROUTINE_IDS
        if exercise_id in exercise_lookup
    ]
    if len(exercises) < 4:
        exercises = [deepcopy(exercise) for exercise in exercise_pool[:4]]

    return {
        "plan_id": f"mr_lim_cardio_core_{level}",
        "persona": deepcopy(MR_LIM_PERSONA),
        "title": "Today's routine: cardio and core",
        "subtitle": "A short low-impact routine to build activity gradually.",
        "level": level,
        "duration_minutes": 6,
        "risk_context": {
            "top_risk": "Heart disease",
            "reason": (
                "Mr Lim rarely exercises and wants one practical next step. "
                "This plan uses low-impact cardio and core movements to support "
                "gradual habit building."
            ),
            "disclaimer": (
                "This routine is general health guidance. It is not medical advice "
                "and does not diagnose or predict individual health outcomes."
            ),
        },
        "exercises": exercises,
        "guidance_tip": {
            "title": "Tip",
            "text": "Move at your own pace and take breaks when you need to.",
        },
        "safety_note": (
            "Start gently. Stop if you feel chest pain, dizziness, unusual shortness "
            "of breath, or sharp pain."
        ),
        "guideline_note": (
            "Exercise recommendations align with Saranan Aktiviti Fizikal Malaysia "
            "and support SDG3 Good Health and Well-Being."
        ),
        "source": {
            "name": "wger.de Exercise Database",
            "licence": "CC-BY-SA / open exercise data",
            "usage": (
                "Exercise names, instructions, categories, equipment and media are "
                "wger-sourced where available. Sets, reps, duration and tips are "
                "HealthAge MVP logic. Data is read from Neon when an exercise table "
                "exists, otherwise the app uses the local curated fallback pool."
            ),
        },
    }


def get_replacement_exercise(current_id: str | None, plan_tag: str = "cardio_core") -> dict[str, Any]:
    """Return a replacement exercise from the same curated MVP pool."""
    exercise_pool = _load_exercise_pool()

    for exercise in exercise_pool:
        if exercise["id"] == current_id:
            continue
        if plan_tag in exercise["plan_tags"] and exercise["id"] not in DEFAULT_ROUTINE_IDS:
            return deepcopy(exercise)

    for exercise in exercise_pool:
        if exercise["id"] != current_id:
            return deepcopy(exercise)

    return deepcopy(exercise_pool[0])


def _load_exercise_pool() -> list[dict[str, Any]]:
    return _database_exercise_pool() or deepcopy(EXERCISE_POOL)


def _database_exercise_pool() -> list[dict[str, Any]]:
    database = settings.DATABASES.get("default", {})
    if database.get("ENGINE") != "django.db.backends.postgresql":
        return []

    try:
        tables = connection.introspection.table_names()
    except DatabaseError:
        return []

    table_lookup = {table.lower(): table for table in tables}
    table = table_lookup.get("exercise")
    if not table:
        return []

    try:
        rows = _fetch_rows(table)
    except DatabaseError:
        return []

    exercises = [_normalise_exercise_row(row) for row in rows if _row_is_active(row)]
    return [exercise for exercise in exercises if exercise]


def _fetch_rows(table: str) -> list[dict[str, Any]]:
    quoted = connection.ops.quote_name(table)
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {quoted} LIMIT %s", [200])
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return sorted(
        rows,
        key=lambda row: (
            _int_or_default(row.get("display_order"), 999),
            _int_or_default(row.get("exercise_id"), 999),
            str(row.get("exercise_key") or row.get("exercise_name") or ""),
        ),
    )


def _normalise_exercise_row(row: dict[str, Any]) -> dict[str, Any] | None:
    exercise_key = str(row.get("exercise_key") or "").strip()
    exercise_name = str(row.get("exercise_name") or row.get("name") or "").strip()
    if not exercise_key or not exercise_name:
        return None

    return {
        "id": exercise_key,
        "wger_id": _int_or_none(row.get("wger_id")),
        "wger_uuid": _str_or_none(row.get("wger_uuid")),
        "name": exercise_name,
        "category": str(row.get("category") or "").strip(),
        "equipment": str(row.get("equipment") or "").strip(),
        "muscles": _list_value(row.get("muscles")),
        "sets": _int_or_default(row.get("sets"), 1),
        "reps": _int_or_none(row.get("reps")),
        "duration_seconds": _int_or_none(row.get("duration_seconds")),
        "instructions": str(row.get("instructions") or "").strip(),
        "image_url": _str_or_none(row.get("image_url")),
        "video_url": _str_or_none(row.get("video_url")),
        "source_url": str(row.get("source_url") or "").strip(),
        "source_note": str(row.get("source_note") or "Exercise data is sourced from the HealthAge exercise table.").strip(),
        "difficulty": str(row.get("difficulty_level") or row.get("difficulty") or "beginner").strip(),
        "plan_tags": _list_value(row.get("plan_tags")) or ["cardio_core"],
    }


def _row_is_active(row: dict[str, Any]) -> bool:
    value = row.get("is_active")
    if value is None:
        return True
    return str(value).strip().lower() not in {"0", "false", "no"}


def _list_value(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("["):
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = []
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in text.split(",") if item.strip()]
    return [str(value).strip()]


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _int_or_default(value: Any, default: int) -> int:
    return _int_or_none(value) or default


def _str_or_none(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None
