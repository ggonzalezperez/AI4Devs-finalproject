# Task PWD-a Report: Change Password + Recovery-Code Reset (Backend)

## Status
DONE

## Commit
SHA: 7076c9a  
Subject: `feat(backend): change password + recovery-code reset (email-free)`

## Tests
**107 passed, 0 failed** (full suite, `python -m pytest -q`)

New tests in `tests/test_password.py` (9 tests):
- `test_register_returns_recovery_code` — format `^[0-9A-F]{4}-[0-9A-F]{4}$` verified
- `test_change_password_wrong_current` — 400 on wrong current password
- `test_change_password_correct` — 200, new login works, old login fails
- `test_change_password_requires_auth` — 401 without token
- `test_reset_password_correct_code` — 200, returns new code in correct format, distinct from old
- `test_reset_password_old_password_rejected_new_accepted` — old pw 401, new pw 200
- `test_reset_password_code_is_rotated` — second reset with old code → 400
- `test_reset_password_wrong_code` — 400
- `test_reset_password_nonexistent_email` — 400

## Migration op.* lines
```python
op.add_column('users', sa.Column('recovery_code_hash', sa.String(length=255), nullable=True))
```
Migration file: `backend/alembic/versions/ad23d09d1b34_user_recovery_code_hash.py`

No `op.drop_column`, `op.alter_column`, or changes to other tables — migration is NON-DESTRUCTIVE.

## Ruff
`All checks passed!` (zero violations on `app` and `tests`)

## Self-Review

| Security requirement | Status |
|---|---|
| Recovery code returned plaintext only at register and only once per reset | PASS — returned in `RegisterResult.recovery_code` at register; returned in `RecoveryResult.recovery_code` at reset; never stored in plain text |
| Recovery code stored as hash | PASS — `user.recovery_code_hash = hash_secret(code)` using bcrypt via `hash_secret()` |
| Rotation invalidates old code | PASS — `reset_password()` generates `new_code`, overwrites `user.recovery_code_hash`; test `test_reset_password_code_is_rotated` confirms old code returns 400 |
| change-password requires correct current password | PASS — `change_password()` calls `verify_secret(current, user.password_hash)`, returns `False` → 400 if incorrect |
| reset-password doesn't leak whether email exists | PASS — when email not found, calls `verify_secret(code, _DUMMY_HASH)` for constant-time cost, returns `None`; endpoint returns 400 in both "email not found" and "wrong code" cases |

## Files Modified
- `backend/app/models/family.py` — added `recovery_code_hash: Mapped[str | None]` to `User`
- `backend/app/schemas/auth.py` — added `RegisterResult`, `ChangePasswordRequest`, `ResetPasswordRequest`, `RecoveryResult`
- `backend/app/services/auth_service.py` — added `import secrets`, `_new_recovery_code()`, updated `register_family()`, added `change_password()` and `reset_password()`
- `backend/app/routers/auth.py` — updated `register` to return `RegisterResult`, added `/change-password` and `/reset-password` endpoints
- `backend/alembic/versions/ad23d09d1b34_user_recovery_code_hash.py` — new migration (add_column only)
- `backend/tests/test_password.py` — new test file (9 tests)
