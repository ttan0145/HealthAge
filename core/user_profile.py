"""Where the dashboard gets the user's age and sex.

Step 1 of onboarding (profile.html) submits to /lifestyle/ as query
parameters. Nothing was reading them, so the statistics always fell back to
a hardcoded persona. This captures them into the session on the way past, so
the dashboard and the statistics endpoint can still read them after the user
has clicked through to step 2.

Session rather than a table on purpose: the team ERD has a User_Profile
table, but the MVP notes on feat/mvp-risk-flow say session storage is
acceptable for this iteration. Swap `capture` and `current` for reads and
writes against that table when it lands, and nothing else has to change.
"""

from core.statistics import DEFAULT_AGE, DEFAULT_GENDER, normalise_gender

SESSION_KEY = 'user_profile'

MIN_AGE = 1
MAX_AGE = 120


def clean_age(value):
    """Return a plausible age, or None if the input cannot be used."""
    try:
        age = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return age if MIN_AGE <= age <= MAX_AGE else None


def capture(request):
    """Store any profile fields present in the query string.

    Only writes fields that are actually present and valid, so landing on a
    page without parameters never wipes an answer the user already gave.
    """
    stored = dict(request.session.get(SESSION_KEY) or {})
    changed = False

    if (age := clean_age(request.GET.get('age'))) is not None:
        stored['age'] = age
        changed = True

    if raw_gender := (request.GET.get('gender') or '').strip():
        stored['gender'] = normalise_gender(raw_gender)
        changed = True

    for field in ('full_name', 'state'):
        if value := (request.GET.get(field) or '').strip():
            stored[field] = value
            changed = True

    if changed:
        request.session[SESSION_KEY] = stored

    return stored


def current(request):
    """The profile to calculate against, falling back to the demo persona."""
    stored = request.session.get(SESSION_KEY) or {}
    return {
        'age': stored.get('age', DEFAULT_AGE),
        'gender': stored.get('gender', DEFAULT_GENDER),
        'full_name': stored.get('full_name', ''),
        'state': stored.get('state', ''),
        # False means the user has not been through step 1 in this session.
        'answered': 'age' in stored or 'gender' in stored,
    }
