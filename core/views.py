from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

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
    return render(request, 'core/index.html')


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
            request.session.modified = True
            return redirect("lifestyle")
    else:
        errors = {}

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
    result = request.session.get("risk_result")
    if not result:
        profile_data = request.session.get("profile")
        lifestyle_data = request.session.get("lifestyle", {"habits": ["Rarely exercise"], "family_history": []})
        if not profile_data:
            return redirect("profile")
        result = build_risk_result(profile_data, lifestyle_data)
        request.session["risk_result"] = result
        request.session.modified = True

    return render(request, "core/dashboard.html", {"result": result})


def readmore(request):
    result = request.session.get("risk_result")
    if not result:
        return redirect("profile")
    return render(request, "core/readmore.html", {"result": result})


def source(request):
    result = request.session.get("risk_result")
    return render(request, "core/source.html", {"result": result})


def stayfit(request):
    result = request.session.get("risk_result")
    return render(request, "core/stayfit.html", {"result": result})


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
