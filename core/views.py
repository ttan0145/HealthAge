from django.http import JsonResponse
from django.shortcuts import redirect, render

from core import user_profile
from core.risk_content import DEFAULT_RISK, get_risk
from core.statistics import cause_in_group, get_statistics, ordinal


def index(request):
    return render(request, 'core/index.html')

def profile(request):
    return render(request, 'core/profile.html')

def lifestyle(request):
    # Step 1 posts its answers here on the way to step 2. Capture them before
    # rendering, otherwise the age and sex are lost for the rest of the flow.
    user_profile.capture(request)
    return render(request, 'core/lifestyle.html')

def dashboard(request):
    # Also capture here so /dashboard/?age=..&gender=.. works for testing and
    # for anyone linking straight to a result.
    user_profile.capture(request)
    return render(request, 'core/dashboard.html', {
        'profile': user_profile.current(request),
    })

def readmore(request):
    """Detail page for one risk, chosen by ?risk=<slug>.

    One template serves every risk. An unknown or missing slug redirects to
    the default rather than 404ing, so a stale link still lands somewhere
    useful.
    """
    slug = request.GET.get('risk', DEFAULT_RISK)
    risk = get_risk(slug)

    if risk is None:
        return redirect(f'/readmore/?risk={DEFAULT_RISK}')

    user_profile.capture(request)
    answers = user_profile.current(request)
    stats = get_statistics(answers['age'], answers['gender'])

    # Where this particular cause sits for this user's group. None means the
    # workbook does not list it in their top ten, which the page says plainly
    # rather than showing a made up rank.
    here = cause_in_group(stats, slug)

    return render(request, 'core/readmore.html', {
        'risk': risk,
        'profile': answers,
        'stats': stats,
        'here': here,
        'here_rank': ordinal(here['rank']) if here else None,
        'is_top_risk': bool(here and here['rank'] == 1),
        # The rest of this group's causes, so the reader can move between them.
        'other_causes': [c for c in stats['causes'] if c['slug'] != slug],
    })

def cause_of_death_stats(request):
    """Backend work 1: user's age and gender in, cause of death stats out.

    Age and sex come from the profile the user filled in at step 1, held in
    the session. Query parameters still override, which keeps the endpoint
    testable and lets a link carry an explicit group.

        /api/cause-of-death/                      -> the session's profile
        /api/cause-of-death/?age=30&gender=Female -> that group
    """
    user_profile.capture(request)
    answers = user_profile.current(request)
    return JsonResponse(get_statistics(answers['age'], answers['gender']))

def source(request):
    return render(request, 'core/source.html')

def stayfit(request):
    return render(request, 'core/stayfit.html')