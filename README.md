# HealthAge

HealthAge is a Django MVP for the FIT5120 onboarding iteration. The application collects a short user profile, combines it with lifestyle inputs, and returns one prioritised health risk, one practical next step, supporting risk information, and source transparency.

The current implementation is designed to run with or without the team Neon database:

- With `DATABASE_URL`, Django connects to Postgres and the risk engine attempts to read the available public health tables.
- Without `DATABASE_URL`, the app uses local fallback logic so the full demo flow still works.

## Current Flow

1. Landing page explains the value proposition and evidence base.
2. Profile intake collects age, sex, and Malaysian state.
3. Lifestyle intake collects habits and family history.
4. Dashboard shows the top risk, one recommended action, other assessed risks, and a non-diagnosis disclaimer.
5. Read More explains the prioritised risk in plain language.
6. Source lists the public datasets used by the MVP.
7. Stay Fit lets the user choose a health focus such as Heart disease, Stroke, Type 2 diabetes, Respiratory disease, or Cancer.
8. Stay Fit renders a dynamic routine for the selected focus, including an exercise list, timer, guidance panel, exercise detail modal, and swap interaction.
9. Stay Fit API returns a stable routine JSON contract for the page, with Neon exercise-table support and a local fallback pool.

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
- `core/stayfit_api.py` builds the Stay Fit routine and reshuffle API payloads.
- `core/static/core/js/stayfit.js` renders the Stay Fit routine, timer, modal and swap interactions.
- `core/static/img/grandpa.png` is the Stay Fit guidance mascot asset integrated from the latest `main` branch.

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

If the team shares split Neon variables instead of one URL, set these keys instead:

```env
DB_NAME=neondb
DB_USER=neondb_owner
DB_PASSWORD=replace-this-locally
DB_HOST=replace-this-locally
DB_PORT=5432
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

Stay Fit API endpoints:

```text
http://127.0.0.1:8000/api/stayfit/routine/
http://127.0.0.1:8000/api/stayfit/routine/?risk=heart_disease
http://127.0.0.1:8000/api/stayfit/reshuffle/?current=step_jack&risk=heart_disease
```

## Stay Fit Collaboration Handoff

The Stay Fit work is split by API/data and frontend interaction:

- Backend/API boundary: `core/stayfit_api.py`, `core/views.py`, `healthrisk/urls.py`, and `docs/sql/stayfit_exercise_seed.sql`.
- Frontend boundary: `core/templates/core/stayfit.html`, `core/static/core/js/stayfit.js`, and the Stay Fit styles in `core/static/core/css/style.css`.
- Shared include logic should stay in `core/static/core/js/include.js`; page-specific timer or modal logic belongs in `stayfit.js`.

Useful handoff documents:

- Chinese API contract: `docs/stayfit-api-contract-zh.md`
- Chinese implementation handoff: `docs/stayfit-handoff-zh.md`

Current Stay Fit status:

- The page shows disease/risk focus buttons and consumes `/api/stayfit/routine/?risk=<risk_key>` instead of hardcoded exercise rows.
- The current supported focus keys are `heart_disease`, `stroke`, `type_2_diabetes`, `respiratory_disease`, and `cancer`.
- The routine API supports three intensity levels through `level=beginner`, `level=standard`, and `level=progress`, displayed as Low, Medium and High.
- The Stay Fit focus choice is not saved to the database or session; it only travels as a request query parameter.
- Exercise order rows select the active guidance exercise only; they do not open the detail modal.
- Exercise details are displayed from the guidance panel modal using image/video fields when available and written instructions as fallback.
- Swap calls `/api/stayfit/reshuffle/` with the current focus and replaces only one exercise row.
- Timer logic is implemented in `stayfit.js`, not in the shared include script, and it does not auto-advance the exercise order.
- The latest `main` mascot image has been integrated into the guidance panel.
- The curated exercise pool contains 26 low-impact movements. Current Neon coverage is at least 10 movements per focus: Heart disease 20, Stroke 22, Type 2 diabetes 15, Respiratory disease 17, and Cancer 22.
- The page prefers local exercise diagrams for known movements so the demo does not depend on incomplete third-party video coverage.

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
- Stay Fit routine API contract, disease-focus routine selection, reshuffle API, and dynamic page hooks.
- Stay Fit database-preferred exercise pool with local fallback.

By default, `manage.py test` uses a local SQLite test database even when Neon environment variables are present. This prevents Django from creating or dropping test databases on the shared Neon project. Set `ALLOW_REMOTE_TEST_DATABASE=True` only if the team explicitly wants to run tests against Postgres.

## Delivery Tracking

User stories are implemented and verified separately so each change can be reviewed and managed independently:

- [US 1.1 - Quick Profile Intake](docs/user-stories/US-1.1-quick-profile-intake.md)

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

Stay Fit does not persist the disease/risk focus selection. The page sends a `risk` query parameter to the API and updates the visible routine only for the current browser request.

Stay Fit exercise data currently supports two modes:

- If a Neon/Postgres `exercise` table exists, `core/stayfit_api.py` reads the curated wger-sourced exercise pool from that table.
- If the table is unavailable, the app uses the local curated fallback pool so the demo remains stable.
- If Neon has only part of the exercise catalogue, matching database rows override local records and the local fallback pool fills missing movements.

The prepared Neon SQL seed is available at `docs/sql/stayfit_exercise_seed.sql`. Review the shared database before running it.

## Development Notes

- Keep UI text, comments, commit messages, and documentation in English.
- Keep secrets out of Git.
- Prefer focused comments that explain non-obvious decisions. Do not add boilerplate comments that restate the code.
- Keep the non-diagnosis disclaimer visible anywhere personalised health results are shown.
- Treat the current matching logic as MVP logic, not clinical advice.
