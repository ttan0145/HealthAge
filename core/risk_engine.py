"""Profile validation and risk result assembly for the MVP flow."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from .health_data_gateway import ActionMapping, fetch_action_mapping, fetch_mortality_match


CAUSE_ALIASES = {
    "heart": "Heart disease",
    "ischaemic": "Heart disease",
    "ischemic": "Heart disease",
    "cardio": "Heart disease",
    "stroke": "Stroke",
    "cerebrovascular": "Stroke",
    "diabetes": "Type 2 diabetes",
    "malignant": "Cancer",
    "cancer": "Cancer",
    "pneumonia": "Respiratory disease",
    "respiratory": "Respiratory disease",
}

RISK_COPY = {
    "Heart disease": {
        "description": "Heart and blood vessel disease is a leading preventable risk for middle-aged adults.",
        "detail": "Heart disease often develops quietly. Screening for blood pressure, cholesterol and diabetes gives a clearer picture of whether lifestyle changes or medical review should come first.",
        "action": "Book a basic health screening",
        "action_detail": "Check blood pressure, cholesterol and blood glucose first; these are common, measurable risk factors.",
    },
    "Stroke": {
        "description": "Stroke risk is closely tied to blood pressure, smoking, diabetes and cholesterol.",
        "detail": "A stroke happens when blood flow to the brain is blocked or a blood vessel bursts. For many adults, the first useful step is checking and controlling blood pressure.",
        "action": "Check your blood pressure this week",
        "action_detail": "Use a clinic or pharmacy reading and follow up with a health professional if it is high.",
    },
    "Type 2 diabetes": {
        "description": "Diabetes risk rises with age, family history, weight, activity level and diet pattern.",
        "detail": "Type 2 diabetes can be present before symptoms are obvious. A blood glucose test is a practical way to know whether further care is needed.",
        "action": "Book a blood glucose test",
        "action_detail": "Ask for a fasting glucose or HbA1c test at a clinic or screening programme.",
    },
    "Cancer": {
        "description": "Cancer risk depends on age, sex, family history and screening eligibility.",
        "detail": "Cancer is not one single condition. The useful next step is to check which screenings are recommended for your age and sex rather than guessing.",
        "action": "Check age-appropriate screening",
        "action_detail": "Review official screening guidance and discuss eligibility with a clinic.",
    },
    "Respiratory disease": {
        "description": "Respiratory risk is influenced by smoking, air quality and existing breathing conditions.",
        "detail": "Persistent cough, breathlessness or smoking history should be discussed with a clinician. Stopping smoking is usually the highest-impact action.",
        "action": "Review breathing symptoms and smoking risk",
        "action_detail": "If you smoke or have persistent symptoms, arrange a clinic review.",
    },
}

DEFAULT_SOURCES = [
    "DOSM Statistics on Causes of Death, 2021 to 2024",
    "NHMS 2023 population risk factor statistics",
    "KKMNOW / ProtectHealth PeKaB40 screening information",
]


@dataclass(frozen=True)
class Profile:
    name: str
    age: int
    sex: str
    state: str


def validate_profile(data: dict[str, Any]) -> tuple[Profile | None, dict[str, str]]:
    errors: dict[str, str] = {}
    name = str(data.get("full_name", "")).strip()
    sex = str(data.get("sex", data.get("gender", ""))).strip()
    state = str(data.get("state", "")).strip()
    age_raw = str(data.get("age", "")).strip()

    if not name:
        errors["full_name"] = "Enter your name."
    try:
        age = int(age_raw)
    except ValueError:
        age = 0
        errors["age"] = "Enter an age as a number."
    else:
        if age < 18 or age > 100:
            errors["age"] = "Age must be between 18 and 100."
    if not sex:
        errors["sex"] = "Choose a sex."
    if not state:
        errors["state"] = "Choose a state."

    if errors:
        return None, errors
    return Profile(name=name, age=age, sex=sex, state=state), {}


def build_risk_result(profile: dict[str, Any], lifestyle: dict[str, list[str]]) -> dict[str, Any]:
    profile_obj = Profile(
        name=profile.get("name", "User"),
        age=int(profile.get("age", 48)),
        sex=profile.get("sex", "Male"),
        state=profile.get("state", "Selangor"),
    )
    habits = lifestyle.get("habits", [])
    family_history = lifestyle.get("family_history", [])

    db_match = fetch_mortality_match(profile_obj.age, profile_obj.sex, profile_obj.state)
    if db_match:
        top_cause = _canonical_cause(db_match.cause_name) or db_match.cause_name
        source_note = _database_source_note(db_match.source_table, db_match.fallback_used)
        mode = "Connected database"
    else:
        top_cause = _fallback_top_cause(profile_obj, habits, family_history)
        source_note = "Using local fallback logic until the Neon DATABASE_URL is available."
        mode = "Local fallback"

    risks = _rank_risks(top_cause, habits, family_history)
    top_risk = risks[0]
    db_action = fetch_action_mapping(db_match.cause_id, top_risk["name"]) if db_match else None
    action = _recommended_action(top_risk["name"], profile_obj, db_action)

    return {
        "mode": mode,
        "profile": {
            "name": profile_obj.name,
            "age": profile_obj.age,
            "sex": profile_obj.sex,
            "state": profile_obj.state,
            "summary": f"{profile_obj.sex}, age {profile_obj.age}, {profile_obj.state}",
        },
        "query_label": f"Comparing {profile_obj.sex.lower()} age {profile_obj.age} in {profile_obj.state} against Malaysian public health data.",
        "top_risk": {
            **top_risk,
            "note": source_note,
            "detail": RISK_COPY[top_risk["name"]]["detail"],
        },
        "recommended_action": action,
        "other_risks": risks[1:],
        "sources": DEFAULT_SOURCES,
        "lifestyle": {
            "habits": habits,
            "family_history": family_history,
        },
    }


def _database_source_note(source_table: str, fallback_used: bool) -> str:
    if fallback_used:
        return f"Matched from Neon table `{source_table}` with a demographic fallback because an exact profile match was unavailable."
    return f"Matched from Neon table `{source_table}` using the closest available demographic fields."


def _canonical_cause(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    lowered = text.lower()
    for needle, canonical in CAUSE_ALIASES.items():
        if needle in lowered:
            return canonical
    return text[:80]


def _fallback_top_cause(profile: Profile, habits: list[str], family_history: list[str]) -> str:
    score = Counter(
        {
            "Heart disease": 4,
            "Stroke": 3,
            "Type 2 diabetes": 2,
            "Cancer": 2,
            "Respiratory disease": 1,
        }
    )

    normalized = " ".join(habits + family_history).lower()
    if "smoking" in normalized:
        score["Respiratory disease"] += 3
        score["Stroke"] += 1
        score["Heart disease"] += 1
    if "rarely exercise" in normalized or "stress" in normalized:
        score["Heart disease"] += 2
        score["Stroke"] += 1
    if "irregular meals" in normalized or "sleep late" in normalized:
        score["Type 2 diabetes"] += 2
    if "diabetes" in normalized:
        score["Type 2 diabetes"] += 3
    if "cancer" in normalized:
        score["Cancer"] += 3
    if profile.age >= 55:
        score["Stroke"] += 1
        score["Cancer"] += 1

    return score.most_common(1)[0][0]


def _rank_risks(top_cause: str, habits: list[str], family_history: list[str]) -> list[dict[str, str]]:
    ordered = [top_cause] + [name for name in RISK_COPY if name != top_cause]
    normalized = " ".join(habits + family_history).lower()
    risks = []

    for index, name in enumerate(ordered[:4]):
        level = "High" if index == 0 else "Moderate" if _is_relevant(name, normalized) else "Baseline"
        risks.append(
            {
                "name": name,
                "level": level,
                "description": RISK_COPY.get(name, RISK_COPY["Heart disease"])["description"],
            }
        )
    return risks


def _is_relevant(name: str, normalized_profile_text: str) -> bool:
    if name == "Heart disease":
        return "stress" in normalized_profile_text or "rarely exercise" in normalized_profile_text
    if name == "Stroke":
        return "smoking" in normalized_profile_text or "stress" in normalized_profile_text
    if name == "Type 2 diabetes":
        return "diabetes" in normalized_profile_text or "irregular meals" in normalized_profile_text
    if name == "Cancer":
        return "cancer" in normalized_profile_text
    if name == "Respiratory disease":
        return "smoking" in normalized_profile_text
    return False


def _recommended_action(cause: str, profile: Profile, db_action: ActionMapping | None = None) -> dict[str, str]:
    if db_action and db_action.action_text:
        return {
            "type": "routine" if db_action.exercise_id else "screening",
            "title": db_action.action_text,
            "subtitle": db_action.rationale or db_action.safety_note or "Follow the curated action mapping for this risk.",
            "target": "/stayfit/" if db_action.exercise_id else "/source/#peka",
            "state": profile.state,
        }

    copy = RISK_COPY.get(cause, RISK_COPY["Heart disease"])
    action_type = "routine" if cause == "Respiratory disease" else "screening"
    target = "/stayfit/" if action_type == "routine" else "/source/#peka"
    return {
        "type": action_type,
        "title": copy["action"],
        "subtitle": copy["action_detail"],
        "target": target,
        "state": profile.state,
    }
