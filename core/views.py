from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from core import user_profile
from core.risk_content import DEFAULT_RISK, get_risk
from core.statistics import cause_in_group, get_statistics, ordinal

from .risk_engine import (
    MALAYSIA_STATES,
    SEX_OPTIONS,
    build_risk_result,
    validate_profile,
)
from .stayfit_api import build_stayfit_routine, get_replacement_exercise

HABIT_OPTIONS = [
    "Smoking",
    "Rarely exercise",
    "Irregular meals",
    "Sleep late",
    "High work stress",
    "No recent screening",
]

FAMILY_HISTORY_OPTIONS = ["Heart disease", "Diabetes", "Cancer"]


def index(request):
    return render(request, "core/index.html")


def profile(request):
    current = request.session.get("profile", {})

    if request.method == "POST":
        profile_obj, errors = validate_profile(request.POST)
        current = {
            "age": request.POST.get("age", "").strip(),
            "sex": request.POST.get("sex", request.POST.get("gender", "")).strip(),
            "state": request.POST.get("state", "").strip(),
        }
        if not errors and profile_obj:
            request.session["profile"] = {
                "age": profile_obj.age,
                "sex": profile_obj.sex,
                "state": profile_obj.state,
            }
            _store_statistics_profile(request, profile_obj.age, profile_obj.sex, profile_obj.state)
            request.session.modified = True
            return redirect("lifestyle")
    else:
        errors = {}
        captured = user_profile.capture(request)
        if captured.get("answered") and not current:
            current = {
                "age": captured.get("age", ""),
                "sex": captured.get("gender", ""),
                "state": captured.get("state", ""),
            }

    return render(
        request,
        "core/profile.html",
        {
            "profile": current,
            "errors": errors,
            "states": MALAYSIA_STATES,
            "sex_options": SEX_OPTIONS,
        },
    )


def lifestyle(request):
    if "profile" not in request.session:
        return redirect("profile")

    current = request.session.get("lifestyle", {})
    errors = {}

    if request.method == "POST":
        habits = list(dict.fromkeys(request.POST.getlist("habits")))
        family_history = list(dict.fromkeys(request.POST.getlist("family_history")))
        current = {
            "habits": habits,
            "family_history": family_history,
        }

        if not habits:
            errors["habits"] = "Choose one or two habits so the recommendation can be prioritised."
        elif len(habits) > 2:
            errors["habits"] = "Choose no more than two habits."
        elif any(habit not in HABIT_OPTIONS for habit in habits):
            errors["habits"] = "Choose habits from the available options."

        if any(condition not in FAMILY_HISTORY_OPTIONS for condition in family_history):
            errors["family_history"] = "Choose conditions from the available options."

        if not errors:
            request.session["lifestyle"] = current
            request.session["risk_result"] = build_risk_result(request.session["profile"], current)
            request.session.modified = True
            return redirect("dashboard")

    return render(
        request,
        "core/lifestyle.html",
        {
            "lifestyle": current,
            "errors": errors,
            "habit_options": HABIT_OPTIONS,
            "family_history_options": FAMILY_HISTORY_OPTIONS,
        },
    )


def dashboard(request):
    user_profile.capture(request)
    return render(
        request,
        "core/dashboard.html",
        {
            "profile": user_profile.current(request),
            "result": _current_risk_result(request),
        },
    )


def readmore(request):
    """Detail page for one risk, chosen by ?risk=<slug>."""
    slug = request.GET.get("risk", DEFAULT_RISK)
    risk = get_risk(slug)

    if risk is None:
        return redirect(f"/readmore/?risk={DEFAULT_RISK}")

    user_profile.capture(request)
    answers = user_profile.current(request)
    stats = get_statistics(answers["age"], answers["gender"])
    here = cause_in_group(stats, slug)

    return render(
        request,
        "core/readmore.html",
        {
            "risk": risk,
            "profile": answers,
            "stats": stats,
            "here": here,
            "here_rank": ordinal(here["rank"]) if here else None,
            "is_top_risk": bool(here and here["rank"] == 1),
            "other_causes": [cause for cause in stats["causes"] if cause["slug"] != slug],
        },
    )


def cause_of_death_stats(request):
    """Return cause-of-death statistics for the current age and gender."""
    user_profile.capture(request)
    answers = user_profile.current(request)
    return JsonResponse(get_statistics(answers["age"], answers["gender"]))


def source(request):
    return render(request, "core/source.html", {"result": _current_risk_result(request)})


def stayfit(request):
    return render(request, "core/stayfit.html", {"result": _current_risk_result(request)})


@require_GET
def api_stayfit_routine(request):
    level = request.GET.get("level", "beginner").strip().lower() or "beginner"
    risk_key = request.GET.get("risk")
    if level not in {"beginner", "standard", "progress"}:
        level = "beginner"
    return JsonResponse(build_stayfit_routine(level=level, risk_key=risk_key))


@require_GET
def api_stayfit_reshuffle(request):
    current_id = request.GET.get("current")
    plan_tag = request.GET.get("plan", "cardio_core").strip().lower() or "cardio_core"
    risk_key = request.GET.get("risk")
    return JsonResponse({"exercise": get_replacement_exercise(current_id, plan_tag=plan_tag, risk_key=risk_key)})


def _store_statistics_profile(request, age, sex, state):
    request.session[user_profile.SESSION_KEY] = {
        "age": age,
        "gender": sex,
        "state": state,
    }


def _current_risk_result(request):
    result = request.session.get("risk_result")
    if result:
        return result

    profile_data = request.session.get("profile")
    if not profile_data:
        return None

    lifestyle_data = request.session.get(
        "lifestyle",
        {"habits": ["Rarely exercise"], "family_history": []},
    )
    result = build_risk_result(profile_data, lifestyle_data)
    request.session["risk_result"] = result
    request.session.modified = True
    return result
