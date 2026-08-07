# US 1.1 - Quick Profile Intake

## Status

Implementation complete on `feat/mvp-risk-flow`. Team and mentor sign-off remain pending.

## Scope

The intake collects only the data needed by the current matching flow:

- Age
- Sex
- Malaysian state
- One or two lifestyle habits
- Optional family history

No login or account creation is required. The user's name is not collected, and submitted values remain in the signed-cookie session rather than being written to the shared database.

## Acceptance Evidence

| Acceptance criterion | Evidence |
| --- | --- |
| Five fields or fewer, with no login | The two-step intake contains five conceptual input groups and no authentication flow. |
| Completion in under 60 seconds | The automated browser flow completed in 10.3 seconds. A timed test with a team member is still required for final sign-off. |
| Missing or invalid values are blocked | Django tests cover invalid age, unknown sex or state, no selected habits, more than two habits, and unknown habit values. |

## Automated Verification

Run:

```powershell
python manage.py check
python manage.py test --noinput
```

Expected result at completion of this story: 10 tests pass.

## Manual Sign-off

- [ ] A test user completes both intake steps in under 60 seconds.
- [ ] The test user confirms that validation messages are clear.
- [ ] The mentor approves the acceptance criteria.
- [ ] The LeanKit card is updated with this evidence.
