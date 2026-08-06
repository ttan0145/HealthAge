# HealthAge

HealthAge is a Django MVP for the FIT5120 onboarding iteration. The application collects a short user profile, combines it with lifestyle inputs, and returns one prioritised health risk, one practical next step, supporting risk information, and source transparency.

The current implementation is designed to run with or without the team Neon database:

- With `DATABASE_URL`, Django connects to Postgres and the risk engine attempts to read the available public health tables.
- Without `DATABASE_URL`, the app uses local fallback logic so the full demo flow still works.

## Current Flow

1. Landing page explains the value proposition and evidence base.
2. Profile intake collects name, age, sex, and Malaysian state.
3. Lifestyle intake collects habits and family history.
4. Dashboard shows the top risk, one recommended action, other assessed risks, and a non-diagnosis disclaimer.
5. Read More explains the prioritised risk in plain language.
6. Source lists the public datasets used by the MVP.
7. Stay Fit provides a minimal starter routine for the exercise action path.

## Project Structure

```text
HealthAge/
  manage.py
  requirements.txt
  .env.example
  healthrisk/
    settings.py
    urls.py
  core/
    views.py
    risk_engine.py
    health_data_gateway.py
    tests.py
    templates/core/
    static/core/
```

Important files:

- `healthrisk/settings.py` reads local environment variables and configures SQLite or Postgres.
- `core/views.py` handles the profile, lifestyle, result, detail, source, and stay-fit pages.
- `core/risk_engine.py` validates profile input and builds the risk result shown on the dashboard.
- `core/health_data_gateway.py` is the reserved database access boundary for the team ERD.
- `core/templates/core/` contains the HTML screens.
- `core/static/core/css/style.css` contains the shared visual system and page styles.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create a local environment file:

```powershell
copy .env.example .env
```

For local fallback mode, leave `DATABASE_URL` empty.

For Neon/Postgres mode, set:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require
SECRET_KEY=replace-this-for-deployment
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,testserver
```

Do not commit `.env`. It may contain database credentials.

## Run Locally

```powershell
python manage.py runserver 127.0.0.1:8000 --noreload
```

Open:

```text
http://127.0.0.1:8000/
```

## Tests

Run the Django test suite:

```powershell
python manage.py test --noinput
```

The current tests cover:

- Invalid profile age validation.
- Profile and lifestyle submission into a dashboard result.
- Read More redirect behavior when no result exists.
- Public Source page rendering.

## Database Notes

The current code reserves interfaces for the ERD shared by the team:

- `User_Profile`: `profile_id`, `age`, `sex`, `location`, `activity_level`, `created_at`
- `Mortality_Record`: `mortality_id`, `cause_id`, `year`, `location`, `age_band`, `sex`, `death_count`, `death_rate`
- `Cause_of_Death`: `cause_id`, `cause_name`, `cause_category`, `cause_code`
- `Match_Result`: `result_id`, `profile_id`, `mortality_id`, `mapping_id`, `fallback_used`, `disclaimer_shown`, `generated_at`
- `Action_Mapping`: `mapping_id`, `cause_id`, `exercise_id`, `action_text`, `rationale`, `safety_note`, `is_active`
- `Exercise`: `exercise_id`, `wger_id`, `exercise_name`, `category`, `equipment`, `instructions`, `difficulty_level`, `source_url`

The live Neon database may still differ from this design. `health_data_gateway.py` currently inspects available table and column names defensively, preferring the ERD names while still tolerating imported names such as `death_records` and `causes_of_death`. Once the team confirms the exact production schema, the gateway should be tightened to explicit SQL queries.

The MVP stores `User_Profile` and `Match_Result` data in the Django session for now. Persisting those records should be added only after the team confirms whether session-only behaviour remains acceptable for the onboarding iteration.

## Development Notes

- Keep UI text, comments, commit messages, and documentation in English.
- Keep secrets out of Git.
- Prefer focused comments that explain non-obvious decisions. Do not add boilerplate comments that restate the code.
- Keep the non-diagnosis disclaimer visible anywhere personalised health results are shown.
- Treat the current matching logic as MVP logic, not clinical advice.
