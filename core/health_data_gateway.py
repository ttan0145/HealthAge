"""Database access boundary for public health datasets.

The MVP keeps user profile and match result data in the session. This module
reserves the database-facing interfaces for the team ERD so the risk engine can
be tightened later without changing views or templates.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.db import DatabaseError, connection


@dataclass(frozen=True)
class MortalityMatch:
    cause_id: int | None
    cause_name: str
    mortality_id: int | None
    source_table: str
    fallback_used: bool


@dataclass(frozen=True)
class ActionMapping:
    action_text: str
    rationale: str
    safety_note: str
    exercise_id: int | None


@dataclass(frozen=True)
class ExerciseRecord:
    exercise_id: int
    exercise_name: str
    category: str
    equipment: str
    instructions: str
    difficulty_level: str
    source_url: str


def fetch_mortality_match(age: int, sex: str, location: str) -> MortalityMatch | None:
    """Return the best mortality match from the ERD-style or imported tables."""
    if not _database_is_configured():
        return None

    try:
        tables = connection.introspection.table_names()
    except DatabaseError:
        return None

    mortality_table = _first_existing_table(tables, ["mortality_record", "death_records", "deaths_by_state_ethnicity"])
    if not mortality_table:
        return None

    try:
        mortality_rows = _sample_table_rows(mortality_table)
    except DatabaseError:
        return None

    if not mortality_rows:
        return None

    cause_lookup = _load_cause_lookup(tables)
    columns = set(mortality_rows[0].keys())
    cause_col = _first_matching_column(columns, ["cause_name", "cause", "cause_of_death", "death_cause", "condition", "disease"])
    cause_id_col = _first_matching_column(columns, ["cause_id"])
    mortality_id_col = _first_matching_column(columns, ["mortality_id", "id"])
    location_col = _first_matching_column(columns, ["location", "state"])
    sex_col = _first_matching_column(columns, ["sex", "gender"])
    age_col = _first_matching_column(columns, ["age_band", "age_group", "age_range", "age"])
    value_col = _first_matching_column(columns, ["death_count", "deaths", "count", "total", "value"])

    scored_rows = _score_mortality_rows(mortality_rows, age, sex, location, location_col, sex_col, age_col)
    if not scored_rows:
        scored_rows = [(row, True) for row in mortality_rows]

    scores: Counter[str] = Counter()
    best_rows: dict[str, tuple[dict[str, Any], bool]] = {}

    for row, fallback_used in scored_rows:
        cause_name = _row_cause_name(row, cause_col, cause_id_col, cause_lookup)
        if not cause_name:
            continue
        scores[cause_name] += _numeric_value(row.get(value_col), default=1)
        best_rows.setdefault(cause_name, (row, fallback_used))

    if not scores:
        return None

    cause_name, _ = scores.most_common(1)[0]
    best_row, fallback_used = best_rows[cause_name]
    return MortalityMatch(
        cause_id=_numeric_value(best_row.get(cause_id_col), default=None),
        cause_name=cause_name,
        mortality_id=_numeric_value(best_row.get(mortality_id_col), default=None),
        source_table=mortality_table,
        fallback_used=fallback_used,
    )


def fetch_action_mapping(cause_id: int | None, cause_name: str) -> ActionMapping | None:
    """Return a curated action mapping when the ERD Action_Mapping table exists."""
    if not _database_is_configured():
        return None

    try:
        tables = connection.introspection.table_names()
    except DatabaseError:
        return None

    table = _first_existing_table(tables, ["action_mapping"])
    if not table:
        return None

    try:
        rows = _sample_table_rows(table, limit=1000)
    except DatabaseError:
        return None

    if not rows:
        return None

    columns = set(rows[0].keys())
    cause_id_col = _first_matching_column(columns, ["cause_id"])
    action_col = _first_matching_column(columns, ["action_text", "action", "recommendation"])
    rationale_col = _first_matching_column(columns, ["rationale", "reason"])
    safety_col = _first_matching_column(columns, ["safety_note", "safety"])
    exercise_id_col = _first_matching_column(columns, ["exercise_id"])
    active_col = _first_matching_column(columns, ["is_active", "active"])

    for row in rows:
        if active_col and str(row.get(active_col)).lower() in {"false", "0", "no"}:
            continue
        if cause_id_col and cause_id is not None and _numeric_value(row.get(cause_id_col), default=-1) != cause_id:
            continue
        if not action_col:
            continue
        return ActionMapping(
            action_text=str(row.get(action_col) or "").strip(),
            rationale=str(row.get(rationale_col) or "").strip(),
            safety_note=str(row.get(safety_col) or "").strip(),
            exercise_id=_numeric_value(row.get(exercise_id_col), default=None),
        )

    return None


def fetch_exercise(exercise_id: int | None) -> ExerciseRecord | None:
    """Return one exercise record for future Stay Fit personalisation."""
    if exercise_id is None or not _database_is_configured():
        return None

    try:
        tables = connection.introspection.table_names()
    except DatabaseError:
        return None

    table = _first_existing_table(tables, ["exercise"])
    if not table:
        return None

    try:
        rows = _sample_table_rows(table, limit=1000)
    except DatabaseError:
        return None

    for row in rows:
        row_id = _numeric_value(row.get("exercise_id"), default=-1)
        if row_id != exercise_id:
            continue
        return ExerciseRecord(
            exercise_id=row_id,
            exercise_name=str(row.get("exercise_name") or "").strip(),
            category=str(row.get("category") or "").strip(),
            equipment=str(row.get("equipment") or "").strip(),
            instructions=str(row.get("instructions") or "").strip(),
            difficulty_level=str(row.get("difficulty_level") or "").strip(),
            source_url=str(row.get("source_url") or "").strip(),
        )

    return None


def _database_is_configured() -> bool:
    database = settings.DATABASES.get("default", {})
    return database.get("ENGINE") == "django.db.backends.postgresql"


def _sample_table_rows(table: str, limit: int = 2000) -> list[dict[str, Any]]:
    quoted = connection.ops.quote_name(table)
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {quoted} LIMIT %s", [limit])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _load_cause_lookup(tables: list[str]) -> dict[int, str]:
    table = _first_existing_table(tables, ["cause_of_death", "causes_of_death"])
    if not table:
        return {}

    try:
        rows = _sample_table_rows(table, limit=2000)
    except DatabaseError:
        return {}

    if not rows:
        return {}

    columns = set(rows[0].keys())
    cause_id_col = _first_matching_column(columns, ["cause_id", "id"])
    name_col = _first_matching_column(columns, ["cause_name", "name", "cause"])
    if not cause_id_col or not name_col:
        return {}

    lookup: dict[int, str] = {}
    for row in rows:
        cause_id = _numeric_value(row.get(cause_id_col), default=None)
        name = str(row.get(name_col) or "").strip()
        if cause_id is not None and name:
            lookup[cause_id] = name
    return lookup


def _score_mortality_rows(
    rows: list[dict[str, Any]],
    age: int,
    sex: str,
    location: str,
    location_col: str | None,
    sex_col: str | None,
    age_col: str | None,
) -> list[tuple[dict[str, Any], bool]]:
    scored = [(row, False) for row in rows]

    if location_col:
        location_rows = [(row, False) for row, _ in scored if _matches_text(row.get(location_col), location)]
        if location_rows:
            scored = location_rows

    if sex_col:
        sex_rows = [(row, fallback) for row, fallback in scored if _matches_text(row.get(sex_col), sex)]
        if sex_rows:
            scored = sex_rows

    if age_col:
        age_rows = [(row, fallback) for row, fallback in scored if _matches_age(row.get(age_col), age)]
        if age_rows:
            scored = age_rows

    if len(scored) == len(rows):
        return [(row, True) for row, _ in scored]
    return scored


def _row_cause_name(
    row: dict[str, Any],
    cause_col: str | None,
    cause_id_col: str | None,
    cause_lookup: dict[int, str],
) -> str:
    if cause_col and row.get(cause_col):
        return str(row.get(cause_col)).strip()

    if cause_id_col:
        cause_id = _numeric_value(row.get(cause_id_col), default=None)
        if cause_id is not None:
            return cause_lookup.get(cause_id, "")

    return ""


def _first_existing_table(tables: list[str], names: list[str]) -> str | None:
    table_lookup = {table.lower(): table for table in tables}
    for name in names:
        if name.lower() in table_lookup:
            return table_lookup[name.lower()]
    return None


def _first_matching_column(columns: set[str], candidates: list[str]) -> str | None:
    lower_lookup = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in lower_lookup:
            return lower_lookup[candidate.lower()]
    for column in columns:
        lowered = column.lower()
        if any(candidate.lower() in lowered for candidate in candidates):
            return column
    return None


def _matches_text(value: Any, expected: str) -> bool:
    if value is None:
        return False
    return str(expected).strip().lower() in str(value).strip().lower()


def _matches_age(value: Any, age: int) -> bool:
    if value is None:
        return False
    text = str(value).lower().replace("to", "-").replace(" ", "")
    if text.isdigit():
        return int(text) == age
    if "-" in text:
        parts = [part for part in text.split("-") if part.isdigit()]
        if len(parts) >= 2:
            return int(parts[0]) <= age <= int(parts[1])
    if "40" in text and "59" in text:
        return 40 <= age <= 59
    if "adult" in text:
        return age >= 18
    return str(age) in text


def _numeric_value(value: Any, default: int | None = 1) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default
