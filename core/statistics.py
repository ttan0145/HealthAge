"""Work 1: cause of death statistics by age band, gender and cause.

Give it an age and a gender, it returns the ranked causes of death for the
matching group, read from the mortality_record table.

Load the data with:

    python manage.py import_cod ~/Downloads/cod_2023.xlsx --year 2023

Note on where this belongs: `core/health_data_gateway.py` on the
feat/mvp-risk-flow branch is the team's designated database boundary. The
tables here use the ERD names (mortality_record, cause_of_death) so that
gateway reads them without changes. When that branch merges, move
_fetch_rows() into the gateway and leave this module doing only the
presentation shaping - ranking, display formatting, and the headline
sentence - which the popup and the read more page both consume.
"""

from core.models import MortalityRecord

DEFAULT_AGE = 48
DEFAULT_GENDER = "Male"
DEFAULT_YEAR = 2023

SOURCE = (
    "Department of Statistics Malaysia, Statistics on Causes of Death 2023, "
    "medically certified deaths"
)

# The workbook publishes causes by sex for ages 15 and over only, so a
# younger profile has nothing to show rather than a risk of zero.
UNAVAILABLE = (
    "Causes of death are not published separately by sex for this age group, "
    "so we cannot show a breakdown here."
)

# The workbook publishes clinical names. These are the plain language versions
# used across the rest of the site; anything not listed is shown as published.
DISPLAY_NAMES = {
    "Ischaemic heart diseases": "Heart disease",
    "Cerebrovascular diseases": "Stroke",
    "Diabetes mellitus": "Type 2 diabetes",
    "Malignant neoplasm of trachea, bronchus and lung": "Lung cancer",
    "Malignant neoplasm of colon, rectum and anus": "Bowel cancer",
    "Malignant neoplasm of breast": "Breast cancer",
    "Malignant neoplasm of liver and intrahepatic bile ducts": "Liver cancer",
    "Malignant neoplasm of ovary": "Ovarian cancer",
    "Malignant neoplasm of cervix uteri": "Cervical cancer",
    "Diseases of the liver": "Liver disease",
    "Hypertensive diseases": "High blood pressure",
    "Chronic lower respiratory diseases": "Chronic lung disease",
    "Respiratory tuberculosis": "Tuberculosis",
}

# Every cause the workbook publishes has a page at /readmore/?risk=<slug>.
# Keys must match cause_name in the database, values must match the keys in
# core/risk_content.py.
CAUSE_SLUGS = {
    "Ischaemic heart diseases": "heart-disease",
    "Cerebrovascular diseases": "stroke",
    "Hypertensive diseases": "high-blood-pressure",
    "Diabetes mellitus": "type-2-diabetes",
    "Pneumonia": "pneumonia",
    "Chronic lower respiratory diseases": "chronic-lung-disease",
    "Respiratory tuberculosis": "tuberculosis",
    "Malignant neoplasm of trachea, bronchus and lung": "lung-cancer",
    "Malignant neoplasm of liver and intrahepatic bile ducts": "liver-cancer",
    "Malignant neoplasm of colon, rectum and anus": "bowel-cancer",
    "Malignant neoplasm of breast": "breast-cancer",
    "Malignant neoplasm of cervix uteri": "cervical-cancer",
    "Malignant neoplasm of ovary": "ovarian-cancer",
    "Leukaemia": "leukaemia",
    "Diseases of the liver": "liver-disease",
    "Transport accidents": "transport-accidents",
    "Intentional self-harm": "intentional-self-harm",
}

# Reverse lookup, for turning a page slug back into its published name.
SLUG_TO_CAUSE = {slug: name for name, slug in CAUSE_SLUGS.items()}

ORDINALS = {1: "1st", 2: "2nd", 3: "3rd"}

# Badge thresholds, by share of all deaths in the group. Drives the existing
# badge--High / --Moderate / --Baseline styles.
HIGH_SHARE = 15.0
MODERATE_SHARE = 3.0


def band_for_age(age):
    """Map a raw age onto one of the bands the workbook publishes."""
    if age < 15:
        return "0-14"
    if age < 41:
        return "15-40"
    if age < 60:
        return "41-59"
    return "60+"


def normalise_gender(gender):
    """Accept 'male', 'M', 'Male' and so on."""
    if not gender:
        return DEFAULT_GENDER
    first = str(gender).strip().lower()[:1]
    return "Female" if first == "f" else "Male"


def format_share(share):
    """17.0 -> '17', 9.5 -> '9.5'. Keeps the wording tidy."""
    return f"{share:g}"


def ordinal(n):
    """1 -> '1st', 4 -> '4th'."""
    return ORDINALS.get(n, f"{n}th")


def cause_in_group(stats, slug):
    """Where one cause sits inside an already calculated group, or None.

    A cause can legitimately be absent: breast cancer does not appear in the
    published top ten for men, so the detail page has to say so rather than
    invent a rank.
    """
    for cause in stats.get("causes", []):
        if cause["slug"] == slug:
            return cause
    return None


def band_label(gender, band):
    """'men aged 41 to 59', 'women aged 60 and over'."""
    group = "men" if gender == "Male" else "women"
    if band.endswith("+"):
        return f"{group} aged {band[:-1]} and over"
    return f"{group} aged {band.replace('-', ' to ')}"


NUMBER_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
                7: "seven", 8: "eight", 9: "nine"}


def subtitle_for(causes, group_total, year):
    """A line that adds scale, without repeating the headline percentage.

    The headline already gives the share, so this gives the absolute count
    and, where it is true, how the top cause compares with the ones below it.
    """
    if not causes:
        return ""

    top = causes[0]
    running = 0.0
    beats = 0
    for cause in causes[1:]:
        running += cause["share"]
        if top["share"] <= running:
            break
        beats += 1

    count = f"{top['death_count']:,}"
    if beats >= 2:
        return (f"{count} deaths in {year}, more than the next "
                f"{NUMBER_WORDS.get(beats, beats)} causes combined.")
    if group_total:
        return f"{count} of the {group_total:,} deaths in this group in {year}."
    return f"{count} deaths in {year}."


def level_for(share):
    if share >= HIGH_SHARE:
        return "High"
    if share >= MODERATE_SHARE:
        return "Moderate"
    return "Baseline"


def _fetch_rows(band, sex, year, location):
    """The database read. Move this into health_data_gateway.py on merge."""
    return list(
        MortalityRecord.objects
        .filter(age_band=band, sex=sex, year=year, location=location,
                certification='medical')
        .select_related('cause')
        .order_by('rank')
    )


def get_statistics(age=DEFAULT_AGE, gender=DEFAULT_GENDER,
                   year=DEFAULT_YEAR, location="Malaysia"):
    """Work 1 entry point: user's age and gender in, ranked causes out.

    Returns the same shape whether or not rows exist, so callers do not have
    to special case an empty group (0-14 is not published by sex).
    """
    try:
        age = int(age)
    except (TypeError, ValueError):
        age = DEFAULT_AGE

    gender = normalise_gender(gender)
    band = band_for_age(age)
    rows = _fetch_rows(band, gender.lower(), year, location)

    causes = [
        {
            "cause": DISPLAY_NAMES.get(row.cause.cause_name, row.cause.cause_name),
            "official_name": row.cause.cause_name,
            "share": row.share_pct,
            "share_display": format_share(row.share_pct),
            "level": level_for(row.share_pct),
            "rank": row.rank,
            "rank_display": ordinal(row.rank),
            "slug": CAUSE_SLUGS.get(row.cause.cause_name),
            "death_count": row.death_count,
            "death_count_display": f"{row.death_count:,}",
        }
        for row in rows
    ]

    # Whatever the published top ten does not account for.
    other_share = None
    if rows:
        counted = sum(row.death_count for row in rows)
        total = rows[0].group_total
        if total:
            other_share = format_share(round((total - counted) / total * 100, 1))

    top = causes[0] if causes else None

    return {
        "age": age,
        "gender": gender,
        "band": band,
        "group_label": band_label(gender, band),
        "causes": causes,
        "available": bool(causes),
        "other_share": other_share,
        "top": top,
        "headline": headline_for(top, gender, band) if causes else UNAVAILABLE,
        "subtitle": subtitle_for(
            causes, rows[0].group_total if rows else None, year),
        "source": SOURCE,
        "year": year,
        "group_total": rows[0].group_total if rows else None,
    }


def headline_for(top, gender, band):
    """The one sentence that replaces the note on the dashboard card."""
    if not top:
        return ""
    # The cause goes after the verb so singular and plural names both read
    # correctly ("is heart disease" / "is transport accidents"). Leading it
    # with the subject would need "is" for one and "are" for the other.
    cause = top["cause"]
    cause = cause[0].lower() + cause[1:] if cause else cause
    return (
        f"The leading cause of death among {band_label(gender, band)} in "
        f"Malaysia is {cause}, at {top['share_display']}% of all deaths in "
        f"that group."
    )
