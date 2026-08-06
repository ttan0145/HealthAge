from django.shortcuts import redirect, render

from .risk_engine import build_risk_result, validate_profile


MALAYSIA_STATES = [
    "Johor",
    "Kedah",
    "Kelantan",
    "Melaka",
    "Negeri Sembilan",
    "Pahang",
    "Penang",
    "Perak",
    "Perlis",
    "Sabah",
    "Sarawak",
    "Selangor",
    "Terengganu",
    "W.P. Kuala Lumpur",
    "W.P. Labuan",
    "W.P. Putrajaya",
]

SEX_OPTIONS = ["Male", "Female"]

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
            "name": request.POST.get("full_name", "").strip(),
            "age": request.POST.get("age", "").strip(),
            "sex": request.POST.get("sex", request.POST.get("gender", "")).strip(),
            "state": request.POST.get("state", "").strip(),
        }
        if not errors and profile_obj:
            request.session["profile"] = {
                "name": profile_obj.name,
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
        habits = request.POST.getlist("habits")
        family_history = request.POST.getlist("family_history")
        if not habits:
            errors["habits"] = "Choose at least one habit so the recommendation can be prioritised."
        else:
            current = {
                "habits": habits,
                "family_history": family_history,
            }
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
