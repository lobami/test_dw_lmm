# Pydantic v2 migration audit

Summary
-------
This project has been audited for Pydantic v2 compatibility. The codebase already uses
`ConfigDict` / `model_config` and `model_dump` APIs in the main schemas and routers, so
most of the migration is already complete.

Files inspected
---------------
- `app/users/schemas.py` — uses `ConfigDict` and `model_config` for `UserRead`.
- `app/campaigns/schemas.py` — uses `ConfigDict` and `model_config` across Campaign models.
- `app/campaigns/routers.py` — uses `model_dump()` when creating campaigns (Pydantic v2 API).

Compatibility notes
-------------------
- No `@validator` or `Config` (v1) usages were found in application code. The project therefore
  does not require mass refactors of validators.
- There are no explicit calls to `BaseModel.dict()` in application code; FastAPI/encoders
  already use compatibility shims where needed. The code uses `model_dump()` where appropriate.

What was done
-------------
- Added this audit file documenting the status.
- Ran the test-suite to validate runtime behavior (all tests pass locally).

Recommendations (optional)
-------------------------
- Pin `pydantic>=2` and `fastapi` to a version that declares Pydantic v2 support in `requirements.txt` or your deployment manifest to avoid accidental downgrades.
- If you later introduce class-level validators, prefer the Pydantic v2 `@field_validator` / `@model_validator` APIs.
