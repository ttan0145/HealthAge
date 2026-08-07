"""Stay Fit routine data contract for the MVP.

This module deliberately returns small curated routines instead of proxying
wger live during the user flow. The exercise facts are wger-sourced where
available; the condition-to-routine mapping, sets, reps, duration and tips are
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
        "plan_tags": ["cardio_core", "mobility", "heart_disease", "stroke", "type_2_diabetes", "respiratory_disease"],
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
        "plan_tags": [
            "cardio_core",
            "strength",
            "heart_disease",
            "stroke",
            "type_2_diabetes",
            "respiratory_disease",
            "cancer",
        ],
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
        "plan_tags": ["cardio_core", "strength", "heart_disease", "type_2_diabetes"],
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
        "plan_tags": ["cardio_core", "strength", "heart_disease", "stroke", "cancer"],
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
        "plan_tags": ["mobility", "cardio_core", "heart_disease", "respiratory_disease", "cancer"],
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
        "plan_tags": ["mobility", "cardio_core", "stroke", "type_2_diabetes", "respiratory_disease", "cancer"],
    },
]


DEFAULT_RISK_KEY = "heart_disease"

RISK_ROUTINES = {
    "heart_disease": {
        "label": "Heart disease",
        "description": "Low-impact cardio plus light strength.",
        "plan_tag": "heart_disease",
        "exercise_ids": ["step_jack", "wall_push_up", "bird_dog", "side_plank_knee"],
        "title": "Heart disease: low-impact cardio and core",
        "subtitle": "A short routine to build activity gradually without high impact.",
        "duration_minutes": 6,
        "reason": (
            "This focus uses steady low-impact movement, light upper-body strength "
            "and simple core control to support gradual activity building."
        ),
        "tip": "Keep the pace conversational. Stop and seek help if chest pain or dizziness appears.",
    },
    "stroke": {
        "label": "Stroke",
        "description": "Controlled mobility, balance and core work.",
        "plan_tag": "stroke",
        "exercise_ids": ["torso_rotation", "bird_dog", "side_plank_knee", "step_jack"],
        "title": "Stroke: mobility and control",
        "subtitle": "A gentle routine focused on controlled movement and stability.",
        "duration_minutes": 6,
        "reason": (
            "This focus uses slow mobility and core-stability movements that are "
            "easy to control and can be paused between sets."
        ),
        "tip": "Move slowly and keep support nearby if balance feels uncertain.",
    },
    "type_2_diabetes": {
        "label": "Type 2 diabetes",
        "description": "Light cardio and strength to support activity habits.",
        "plan_tag": "type_2_diabetes",
        "exercise_ids": ["step_jack", "wall_push_up", "bird_dog", "torso_rotation"],
        "title": "Type 2 diabetes: cardio and strength starter",
        "subtitle": "A beginner routine that mixes movement, strength and mobility.",
        "duration_minutes": 7,
        "reason": (
            "This focus combines simple cardio with light strength work because "
            "regular activity is a practical first habit for metabolic health."
        ),
        "tip": "Start after a light warm-up and keep water nearby.",
    },
    "respiratory_disease": {
        "label": "Respiratory disease",
        "description": "Breathing-led mobility at an easy pace.",
        "plan_tag": "respiratory_disease",
        "exercise_ids": ["deep_breathing", "torso_rotation", "step_jack", "bird_dog"],
        "title": "Respiratory disease: breathing and mobility",
        "subtitle": "A gentle routine that starts with breathing and avoids high intensity.",
        "duration_minutes": 6,
        "reason": (
            "This focus starts with breathing control, then adds low-intensity "
            "mobility and short movement blocks."
        ),
        "tip": "Use a slower pace than usual and pause if breathing becomes uncomfortable.",
    },
    "cancer": {
        "label": "Cancer",
        "description": "Gentle mobility and core activation.",
        "plan_tag": "cancer",
        "exercise_ids": ["deep_breathing", "torso_rotation", "bird_dog", "side_plank_knee"],
        "title": "Cancer: gentle mobility starter",
        "subtitle": "A low-pressure routine for general movement and body awareness.",
        "duration_minutes": 6,
        "reason": (
            "This focus keeps the routine gentle and avoids intense loading. It is "
            "only general activity support, not cancer treatment guidance."
        ),
        "tip": "Keep the effort light and check with a clinician if you are in active treatment.",
    },
}

RISK_ALIASES = {
    "heart": "heart_disease",
    "heart_disease": "heart_disease",
    "cardio": "heart_disease",
    "stroke": "stroke",
    "diabetes": "type_2_diabetes",
    "type_2_diabetes": "type_2_diabetes",
    "type2_diabetes": "type_2_diabetes",
    "respiratory": "respiratory_disease",
    "respiratory_disease": "respiratory_disease",
    "cancer": "cancer",
}

DEFAULT_ROUTINE_IDS = RISK_ROUTINES[DEFAULT_RISK_KEY]["exercise_ids"]


def build_stayfit_routine(level: str = "beginner", risk_key: str | None = None) -> dict[str, Any]:
    """Return the stable JSON contract consumed by the Stay Fit frontend."""
    selected_key = _normalise_risk_key(risk_key)
    routine_config = RISK_ROUTINES[selected_key]
    exercise_pool = _load_exercise_pool()
    exercises = _select_exercises(exercise_pool, routine_config["exercise_ids"])

    return {
        "plan_id": f"mr_lim_{selected_key}_{level}",
        "persona": deepcopy(MR_LIM_PERSONA),
        "risk_options": _risk_options(),
        "selected_risk": {
            "key": selected_key,
            "label": routine_config["label"],
            "description": routine_config["description"],
        },
        "plan_tag": routine_config["plan_tag"],
        "title": routine_config["title"],
        "subtitle": routine_config["subtitle"],
        "level": level,
        "duration_minutes": routine_config["duration_minutes"],
        "risk_context": {
            "risk_key": selected_key,
            "top_risk": routine_config["label"],
            "reason": routine_config["reason"],
            "disclaimer": (
                "This routine is general health guidance. It is not medical advice "
                "and does not diagnose or predict individual health outcomes."
            ),
        },
        "exercises": exercises,
        "guidance_tip": {
            "title": "Tip",
            "text": routine_config["tip"],
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


def get_replacement_exercise(
    current_id: str | None,
    plan_tag: str = "cardio_core",
    risk_key: str | None = None,
) -> dict[str, Any]:
    """Return a replacement exercise from the same curated MVP pool."""
    selected_key = _normalise_risk_key(risk_key)
    routine_ids = set(RISK_ROUTINES[selected_key]["exercise_ids"])
    preferred_tag = plan_tag or RISK_ROUTINES[selected_key]["plan_tag"]
    if preferred_tag == "cardio_core" and selected_key != DEFAULT_RISK_KEY:
        preferred_tag = RISK_ROUTINES[selected_key]["plan_tag"]
    exercise_pool = _load_exercise_pool()

    for exercise in exercise_pool:
        if exercise["id"] == current_id:
            continue
        if preferred_tag in exercise["plan_tags"] and exercise["id"] not in routine_ids:
            return deepcopy(exercise)

    for exercise in exercise_pool:
        if exercise["id"] != current_id:
            return deepcopy(exercise)

    return deepcopy(exercise_pool[0])


def _load_exercise_pool() -> list[dict[str, Any]]:
    return _database_exercise_pool() or deepcopy(EXERCISE_POOL)


def _normalise_risk_key(value: str | None) -> str:
    key = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    return RISK_ALIASES.get(key, DEFAULT_RISK_KEY)


def _risk_options() -> list[dict[str, str]]:
    return [
        {
            "key": key,
            "label": routine["label"],
            "description": routine["description"],
        }
        for key, routine in RISK_ROUTINES.items()
    ]


def _select_exercises(exercise_pool: list[dict[str, Any]], exercise_ids: list[str]) -> list[dict[str, Any]]:
    exercise_lookup = {exercise["id"]: exercise for exercise in exercise_pool}
    exercises = [
        deepcopy(exercise_lookup[exercise_id])
        for exercise_id in exercise_ids
        if exercise_id in exercise_lookup
    ]

    if len(exercises) >= 4:
        return exercises[:4]

    selected_ids = {exercise["id"] for exercise in exercises}
    for exercise in exercise_pool:
        if exercise["id"] not in selected_ids:
            exercises.append(deepcopy(exercise))
            selected_ids.add(exercise["id"])
        if len(exercises) == 4:
            break

    return exercises


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
