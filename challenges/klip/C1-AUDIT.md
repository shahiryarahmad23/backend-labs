# C1 Audit — Klip

## 1. Header

- Repo path: `/home/shahiryar_ahmad/projects/backend-labs/challenges/klip`
- The `.git` directory lives one level up at `/home/shahiryar_ahmad/projects/backend-labs`, so git commands cover the whole `backend-labs/` monorepo, not just `challenges/klip/`. Every git observation in this report is qualified accordingly.
- Branch: `main` (only branch)
- HEAD: `bfc5852`
- Audit date: 2026-09-08
- Python files under `src/`: 26 · Total lines under `src/`: 849 (of which the `klip` package itself is 821 lines; `src/domain/retention.py` adds 28)
- Package root is `src/klip/`, not `app/`. Every layering grep in section 2 was retargeted from `app/…` to `src/klip/…` so the checks still apply.
- This audit is static. It could determine layering, missing pieces, wrong dunders/typos/comparators, DB constraints in migrations, and the lint gate. It could not determine: whether Postgres actually starts, whether migrations actually apply, whether the seed command's memory stays flat (there is no seed command), or whether connections are actually released under a raising route. Those go in section 6.

---

## 2. Layering audit

### `fastapi` imports outside the API layer

```
$ rg -l "fastapi" src/klip/services/ src/klip/core/ src/klip/models/ src/klip/schemas/
src/klip/services/user_service.py
src/klip/services/auth_service.py
```

- [src/klip/services/user_service.py:3](src/klip/services/user_service.py:3) — `from fastapi.security import OAuth2PasswordRequestForm`. Services layer knows about the wire protocol. Violation.
- [src/klip/services/auth_service.py:3](src/klip/services/auth_service.py:3) — same import. Violation.

### `HTTPException` outside the API layer

```
$ rg -n "HTTPException" src/klip/
```

Every hit is under `src/klip/api/`:
- [src/klip/api/deps.py:5](src/klip/api/deps.py:5), [src/klip/api/deps.py:14](src/klip/api/deps.py:14), [src/klip/api/deps.py:51](src/klip/api/deps.py:51)
- [src/klip/api/v1/routes_auth.py:2](src/klip/api/v1/routes_auth.py:2), [src/klip/api/v1/routes_auth.py:19](src/klip/api/v1/routes_auth.py:19), [src/klip/api/v1/routes_auth.py:31](src/klip/api/v1/routes_auth.py:31), [src/klip/api/v1/routes_auth.py:41](src/klip/api/v1/routes_auth.py:41)
- [src/klip/api/v1/routes_snippet.py:1](src/klip/api/v1/routes_snippet.py:1), [src/klip/api/v1/routes_snippet.py:44](src/klip/api/v1/routes_snippet.py:44), [src/klip/api/v1/routes_snippet.py:59](src/klip/api/v1/routes_snippet.py:59), [src/klip/api/v1/routes_snippet.py:72](src/klip/api/v1/routes_snippet.py:72), [src/klip/api/v1/routes_snippet.py:75](src/klip/api/v1/routes_snippet.py:75)

No `HTTPException` outside `src/klip/api/`. Passes this specific check.

### `status_code` outside the API layer

Every hit is under `src/klip/api/` (see [src/klip/api/deps.py:15](src/klip/api/deps.py:15), [src/klip/api/deps.py:52](src/klip/api/deps.py:52), [src/klip/api/v1/routes_snippet.py:26](src/klip/api/v1/routes_snippet.py:26), [src/klip/api/v1/routes_snippet.py:44](src/klip/api/v1/routes_snippet.py:44), [src/klip/api/v1/routes_snippet.py:59](src/klip/api/v1/routes_snippet.py:59), [src/klip/api/v1/routes_snippet.py:62](src/klip/api/v1/routes_snippet.py:62), [src/klip/api/v1/routes_snippet.py:72](src/klip/api/v1/routes_snippet.py:72), [src/klip/api/v1/routes_snippet.py:75](src/klip/api/v1/routes_snippet.py:75), [src/klip/api/v1/routes_auth.py:20](src/klip/api/v1/routes_auth.py:20), [src/klip/api/v1/routes_auth.py:26](src/klip/api/v1/routes_auth.py:26), [src/klip/api/v1/routes_auth.py:31](src/klip/api/v1/routes_auth.py:31), [src/klip/api/v1/routes_auth.py:41](src/klip/api/v1/routes_auth.py:41), [src/klip/api/v1/routes_auth.py:57](src/klip/api/v1/routes_auth.py:57)). Passes.

### `core/` importing project code

```
$ rg -n "^from klip|^import klip" src/klip/core/
src/klip/core/security.py:9:from klip.core import settings
```

This is `klip.core.security` importing from `klip.core` — a within-layer re-entry through the package `__init__.py`, not core reaching into another layer. Not a layering violation, but note the fragility: [src/klip/core/__init__.py:1](src/klip/core/__init__.py:1) imports `settings` before line 2 imports the security module that in turn imports `settings` back through the package — this works only because line 1 executes first. Any reorder in `__init__.py` will produce a partially-initialised-module ImportError.

### File sizes under `src/`

| File | Lines |
|---|---|
| [src/klip/services/snippet_service.py](src/klip/services/snippet_service.py) | 124 |
| [src/klip/services/auth_service.py](src/klip/services/auth_service.py) | 102 |
| [src/klip/api/v1/routes_snippet.py](src/klip/api/v1/routes_snippet.py) | 75 |
| [src/klip/services/user_service.py](src/klip/services/user_service.py) | 64 |
| [src/klip/api/v1/routes_auth.py](src/klip/api/v1/routes_auth.py) | 64 |
| [src/klip/core/security.py](src/klip/core/security.py) | 58 |
| [src/klip/api/deps.py](src/klip/api/deps.py) | 54 |
| [src/klip/schemas/user.py](src/klip/schemas/user.py) | 45 |
| [src/klip/models/user.py](src/klip/models/user.py) | 34 |
| [src/klip/models/snippet.py](src/klip/models/snippet.py) | 34 |
| [src/klip/schemas/snippet.py](src/klip/schemas/snippet.py) | 30 |
| [src/domain/retention.py](src/domain/retention.py) | 28 |
| [src/klip/exceptions/exception.py](src/klip/exceptions/exception.py) | 26 |
| [src/klip/models/refresh_token.py](src/klip/models/refresh_token.py) | 22 |
| [src/klip/core/config.py](src/klip/core/config.py) | 18 |
| [src/klip/db/session.py](src/klip/db/session.py) | 15 |
| [src/klip/main.py](src/klip/main.py) | 14 |
| [src/klip/core/__init__.py](src/klip/core/__init__.py) | 11 |
| [src/klip/exceptions/__init__.py](src/klip/exceptions/__init__.py) | 9 |
| [src/klip/services/__init__.py](src/klip/services/__init__.py) | 8 |
| [src/klip/db/base.py](src/klip/db/base.py) | 5 |
| [src/klip/models/__init__.py](src/klip/models/__init__.py) | 3 |
| [src/klip/db/__init__.py](src/klip/db/__init__.py) | 2 |
| [src/klip/schemas/__init__.py](src/klip/schemas/__init__.py) | 2 |
| [src/klip/api/v1/__init__.py](src/klip/api/v1/__init__.py) | 2 |
| [src/klip/api/__init__.py](src/klip/api/__init__.py) | 0 |
| [src/klip/__init__.py](src/klip/__init__.py) | 0 |

No file is oversized.

Note: `src/domain/retention.py` sits outside the `klip` package tree entirely, in a separate top-level package. C10's `Retention` therefore is not part of `klip` and is not importable by anything inside it without adjusting `sys.path` or reorganising the layout. See row C10 in the requirement table and defect D-11.

---

## 3. Requirement table

| ID | Verdict | Evidence (file:line) | Note |
|---|---|---|---|
| A1 | PASS | [docker-compose.yml:5-13](docker-compose.yml:5) | Postgres 16 on host port 5435, named volume `klipdata:/var/lib/postgresql/data` at [docker-compose.yml:12-13](docker-compose.yml:12) and [docker-compose.yml:15-16](docker-compose.yml:16); volume persists across `docker compose up/down`. |
| A2 | PARTIAL | [src/klip/core/config.py:4-18](src/klip/core/config.py:4) | Nine typed required fields, none with defaults, instantiated at import ([src/klip/core/config.py:18](src/klip/core/config.py:18)) — that half is right. But [src/klip/core/config.py:15](src/klip/core/config.py:15) sets `env_file=".env"` as a plain relative string, so the file is only found when the process's CWD happens to be the repo root; run from anywhere else, every required field is missing and the process refuses to start not because the environment is wrong but because the `.env` was not located. Should be `__file__`-anchored. |
| A3 | PASS | [src/klip/main.py:12-14](src/klip/main.py:12) | `GET /health` returns a literal 200. Body is `{"Status : okay"}` — that is a Python **set literal** (one string element), which FastAPI serialises to `["Status : okay"]`. Fits "returns 200 and nothing meaningful" exactly, but was almost certainly meant as a dict (`{"Status": "okay"}`); flagged as hygiene defect D-9. |
| A4 | PASS | [src/klip/core/__init__.py:1-11](src/klip/core/__init__.py:1), [src/klip/db/__init__.py:1-2](src/klip/db/__init__.py:1), [src/klip/models/__init__.py:1-3](src/klip/models/__init__.py:1), [src/klip/schemas/__init__.py:1-2](src/klip/schemas/__init__.py:1), [src/klip/exceptions/__init__.py:1-9](src/klip/exceptions/__init__.py:1), [src/klip/services/__init__.py:1-8](src/klip/services/__init__.py:1) | `api/`, `models/`, `schemas/`, `core/`, `db/`, `services/`, `exceptions/` are present; each `__init__.py` re-exports the public surface, and callers use `from klip.core import …`, `from klip.models import …` etc. — see [src/klip/services/auth_service.py:7-20](src/klip/services/auth_service.py:7). |
| A5 | PASS | grep for `create_all` and `Base.metadata` returns only [migrations/env.py:25](migrations/env.py:25) `target_metadata = Base.metadata` — that is the Alembic target, not a runtime `create_all`. [src/klip/main.py](src/klip/main.py) creates a `FastAPI()` and mounts routers; no startup schema creation. `alembic_version` tracking is stock Alembic (see migration chain: `48a9ebaf1d82 → 8c0bfa168e54 → de8a104e89c6 → 30f84b793702 → 9fc79e201f55`). | |
| A6 | FAIL | [pyproject.toml:32-38](pyproject.toml:32) and `ruff check` output | Config exists (`[tool.ruff]`, `[tool.ruff.lint]`) — but `.venv/bin/ruff check src/` reports **33 errors** across 8 rule codes: 15×F401 (unused re-exports without `# noqa: F401` on the right line, e.g. [src/klip/services/__init__.py:1](src/klip/services/__init__.py:1)), 11×I001 unsorted imports, 2×B904, 1×E401, 1×E711 at [src/klip/services/snippet_service.py:42](src/klip/services/snippet_service.py:42), 1×F811 at [src/klip/services/__init__.py:2](src/klip/services/__init__.py:2), 1×UP042 at [src/klip/models/user.py:12](src/klip/models/user.py:12), 1×UP039 at [src/domain/retention.py:1](src/domain/retention.py:1). The lint gate does not pass. Independently, [pyproject.toml:38](pyproject.toml:38) ignores `B008` with no accompanying reason in the file or a PR message — the spec key calls this out explicitly as the trap. |
| B1 | PASS | [src/klip/core/security.py:6](src/klip/core/security.py:6), [src/klip/core/security.py:11-15](src/klip/core/security.py:11) | Argon2 via `argon2.PasswordHasher`; `password_hash()` calls `.hash()` which generates a random salt per password. Two users with the same password produce distinct stored strings. |
| B2 | PARTIAL | [src/klip/services/user_service.py:19-26](src/klip/services/user_service.py:19), [src/klip/models/user.py:21](src/klip/models/user.py:21), [migrations/versions/48a9ebaf1d82_user_table.py:26](migrations/versions/48a9ebaf1d82_user_table.py:26) | Pre-insert `SELECT` check raises `ValueError("Email already exist")`, which [src/klip/api/v1/routes_auth.py:30-31](src/klip/api/v1/routes_auth.py:30) converts to 409. Works on the happy path, but: (a) the `email` column has **no `unique=True`** on the model and **no unique constraint** in the migration, so a concurrent double-insert produces two rows with the same email and the second returns 201 rather than 409 — the "409 not 500 not success" contract holds only for serial requests; (b) [src/klip/api/v1/routes_auth.py:31](src/klip/api/v1/routes_auth.py:31) uses `detail=str(e)` which leaks the internal message "Email already exist" verbatim to the client. |
| B3 | PASS | [src/klip/api/v1/routes_auth.py:34-41](src/klip/api/v1/routes_auth.py:34) → [src/klip/services/auth_service.py:34-48](src/klip/services/auth_service.py:34) | Login returns `TokenPair(access_token, refresh_token)`: short-lived HS256 JWT ([src/klip/core/security.py:25-29](src/klip/core/security.py:25), expiry from `access_token_expires`) and long-lived opaque URL-safe random from `secrets.token_urlsafe(32)` ([src/klip/core/security.py:39-40](src/klip/core/security.py:39)). |
| B4 | PASS | [src/klip/services/auth_service.py:51-80](src/klip/services/auth_service.py:51) | `refresh_access_token` reads the row, sets `token_row.revoked_at = datetime.now(UTC)` at [src/klip/services/auth_service.py:70](src/klip/services/auth_service.py:70), constructs a new `RefreshTable` at [src/klip/services/auth_service.py:72-76](src/klip/services/auth_service.py:72), then a single `db.commit()` at [src/klip/services/auth_service.py:78](src/klip/services/auth_service.py:78) flushes revoke+issue atomically. Same transaction. A second call presenting the same raw token hits [src/klip/services/auth_service.py:61-62](src/klip/services/auth_service.py:61) and raises `RevokedRefreshToken`. |
| B5 | PASS | [src/klip/core/security.py:43-44](src/klip/core/security.py:43), [src/klip/services/auth_service.py:39-43](src/klip/services/auth_service.py:39), [src/klip/models/refresh_token.py:17](src/klip/models/refresh_token.py:17) | Column is `hashed_token` (not `refresh_token`). Only `hashlib.sha256(token.encode()).hexdigest()` is written; the raw token from `secrets.token_urlsafe` is returned to the client and dropped. Verification hashes the incoming raw token and compares digests at [src/klip/services/auth_service.py:53-57](src/klip/services/auth_service.py:53). |
| B6 | PASS | [src/klip/services/auth_service.py:83-102](src/klip/services/auth_service.py:83), [src/klip/api/v1/routes_auth.py:57-59](src/klip/api/v1/routes_auth.py:57) | Every path — unknown token, already revoked, expired, and success — returns `None` and the route declares `status_code=204`. Indistinguishable to the caller. |
| B7 | PASS | [src/klip/schemas/user.py:14-19](src/klip/schemas/user.py:14), [src/klip/api/v1/routes_auth.py:44-46](src/klip/api/v1/routes_auth.py:44) | `UserRead` declares only `id`, `email`, `role`; `model_config = ConfigDict(from_attributes=True)` at [src/klip/schemas/user.py:19](src/klip/schemas/user.py:19). Route returns `current` typed as `User`, filtered through `response_model=UserRead`. `hashed_password` is not projected. |
| B8 | FAIL | [src/klip/api/deps.py:49-54](src/klip/api/deps.py:49), [src/klip/services/snippet_service.py:114-120](src/klip/services/snippet_service.py:114), [src/klip/api/v1/routes_auth.py:6](src/klip/api/v1/routes_auth.py:6), [src/klip/api/v1/routes_snippet.py:62-75](src/klip/api/v1/routes_snippet.py:62) | The spec requires "one place, referenced by the routes that need it — not repeated inside each route body." What exists is (a) a `require_admin` dependency in `deps.py` that is **imported** by `routes_auth.py` and **not called** by any endpoint, and is also **structurally broken** — [src/klip/api/deps.py:49](src/klip/api/deps.py:49) declares `def require_admin(current_user: User)` with no `Depends(get_current_user)`, so if FastAPI wired it in it would try to resolve `current_user` from the query string; and (b) an inline role branch inside the service at [src/klip/services/snippet_service.py:114-119](src/klip/services/snippet_service.py:114). The check is neither in one place nor referenced by the routes needing it. The lone route that would use it — `DELETE /snippet/{public_id}` — does not. |
| C1 | PASS | [src/klip/models/snippet.py:18-34](src/klip/models/snippet.py:18) | `owner_id` FK to `User.id`, `body`, `title`, `visibility`, `created_at`, `expires_at` (nullable). |
| C2 | PASS | [src/klip/models/snippet.py:28-30](src/klip/models/snippet.py:28), [migrations/versions/de8a104e89c6_snippet_table.py:29](migrations/versions/de8a104e89c6_snippet_table.py:29) | Migration creates a PostgreSQL `ENUM` type `visiblevalue` with members `('PUBLIC','UNLISTED','PRIVATE')`. A raw `INSERT` with a fourth value is rejected by Postgres, not just by Pydantic. Note: because `VisibleValue(str, Enum)` has lowercase values but SQLAlchemy's `Enum` stores `enum.name` by default, values on disk are uppercase — the checklist item that inserts an invalid value in `psql` passes, but an `INSERT` of the string `'public'` will also be rejected; the ORM inserts `'PUBLIC'`. Confirm in section 6. |
| C3 | PASS | [src/klip/models/snippet.py:31-33](src/klip/models/snippet.py:31), [migrations/versions/de8a104e89c6_snippet_table.py:30](migrations/versions/de8a104e89c6_snippet_table.py:30) | `DateTime(timezone=True)` and `server_default=func.now()` on the model; migration emits `sa.DateTime(timezone=True), server_default=sa.text('now()')`. No Python-side `datetime.now()` default anywhere on this column. |
| C4 | PASS | [src/klip/services/snippet_service.py:3](src/klip/services/snippet_service.py:3), [src/klip/services/snippet_service.py:18](src/klip/services/snippet_service.py:18) | `import secrets` and `public = secrets.token_urlsafe(32)` — cryptographically unguessable, URL-safe. Not derived from the primary key. Sequential enumeration is not possible. Caveat noted as D-8: `public_id` has **no `unique=True`** on the column ([src/klip/models/snippet.py:25](src/klip/models/snippet.py:25)) or the index ([migrations/versions/30f84b793702_snippet_table_public_key_added.py:25](migrations/versions/30f84b793702_snippet_table_public_key_added.py:25)) — collision is astronomically unlikely at 32 bytes but the DB does not enforce it. |
| C5 | PASS | [src/klip/schemas/snippet.py:9-13](src/klip/schemas/snippet.py:9), [src/klip/api/v1/routes_snippet.py:26-32](src/klip/api/v1/routes_snippet.py:26), [src/klip/services/snippet_service.py:16-27](src/klip/services/snippet_service.py:16) | `SnippetCreate` has no `owner_id` field. The route resolves `current_user` via `Depends(get_current_user)` and passes it to the service, which writes `owner_id=current_user.id`. Body cannot supply the owner. |
| C6 | PARTIAL | [src/klip/services/snippet_service.py:36-61](src/klip/services/snippet_service.py:36) | Branching is present: not-found ([src/klip/services/snippet_service.py:42-43](src/klip/services/snippet_service.py:42)), expired ([src/klip/services/snippet_service.py:45-46](src/klip/services/snippet_service.py:45)), public any ([src/klip/services/snippet_service.py:48-49](src/klip/services/snippet_service.py:48)), unlisted any-with-id ([src/klip/services/snippet_service.py:51-52](src/klip/services/snippet_service.py:51)), private owner-only ([src/klip/services/snippet_service.py:54-59](src/klip/services/snippet_service.py:54)), private-not-yours ([src/klip/services/snippet_service.py:61](src/klip/services/snippet_service.py:61)). **But** [src/klip/services/snippet_service.py:45](src/klip/services/snippet_service.py:45) compares `snippet.expires_at < datetime.now(UTC)` unconditionally, and `expires_at` is nullable ([src/klip/models/snippet.py:34](src/klip/models/snippet.py:34)) — for any snippet without an expiry (the common case for public/unlisted/private snippets meant to be persistent), that comparison raises `TypeError: '<' not supported between instances of 'NoneType' and 'datetime.datetime'`, FastAPI turns it into a 500, and the route never reaches the visibility branches. The four C6 cases are only exercisable when every snippet has been given an explicit `expires_at`. |
| C7 | PASS | [src/klip/api/v1/routes_snippet.py:35-44](src/klip/api/v1/routes_snippet.py:35) | All three of `ExpiredSnippet`, `PrivateSnippet`, `SnippetNotFound` are caught in the same `except` tuple at [src/klip/api/v1/routes_snippet.py:43](src/klip/api/v1/routes_snippet.py:43) and re-raised as `HTTPException(status_code=404, detail="Not Found")`. Same status, same body, byte-identical. Note the timing side-channel from the spec commentary still exists — the private-not-yours and expired paths do a DB round-trip while the never-existed path returns after the same `SELECT`, so all three actually take similar time here (weakly good). |
| C8 | PARTIAL | [src/klip/api/v1/routes_snippet.py:47-55](src/klip/api/v1/routes_snippet.py:47), [src/klip/services/snippet_service.py:64-104](src/klip/services/snippet_service.py:64) | Server-side cap: `Query(default=settings.default_page_size, le=settings.max_page_size, ge=1)` — a client passing `?limit=10000000` gets a 422, not the honoured value. Owner-only filter and `order_by(created_at.desc(), id.desc())` are correct. Cursor pagination implemented. **But** [src/klip/services/snippet_service.py:89-90](src/klip/services/snippet_service.py:89) raises `SnippetNotFound` when the caller has zero snippets; the route ([src/klip/api/v1/routes_snippet.py:58-59](src/klip/api/v1/routes_snippet.py:58)) turns that into a 404. An empty list is not "not found" — it is an empty page. First-page-empty and end-of-cursor cases both incorrectly 404. |
| C9 | FAIL | [src/klip/api/v1/routes_snippet.py:62-75](src/klip/api/v1/routes_snippet.py:62), [src/klip/services/snippet_service.py:107-122](src/klip/services/snippet_service.py:107) | Service raises `SnippetForbidden` for non-owner and `SnippetNotFound` for missing. The route catches both, then at [src/klip/api/v1/routes_snippet.py:71](src/klip/api/v1/routes_snippet.py:71) does `if e == SnippetForbidden:` — comparing an exception **instance** to the **class**. `Exception.__eq__` falls back to identity, so this is always `False`. Same at [src/klip/api/v1/routes_snippet.py:74](src/klip/api/v1/routes_snippet.py:74). Both branches are dead: the `except` swallows the exception and the function returns `None`, which FastAPI serialises as **204 No Content**. Net effect: deleting someone else's snippet returns 204 (without deleting anything), and deleting a non-existent id returns 204 (without deleting anything). If the comparison were fixed, [src/klip/api/v1/routes_snippet.py:72](src/klip/api/v1/routes_snippet.py:72) would then crash with `TypeError` because `HTTPException` has no `details` kwarg — the actual arg is `detail` (typo in both branches). And even the semantically-correct target for C9 is not 403 — the spec requires the ordinary-caller-non-owner path to be **indistinguishable from "not found"**, i.e. same 404 as C7. |
| C10 | PARTIAL | [src/domain/retention.py:1-28](src/domain/retention.py:1) | `__eq__` guards `isinstance` and returns `NotImplemented` on mismatch, compares `(bytes, plan)` tuple ([src/domain/retention.py:13-17](src/domain/retention.py:13)). `__hash__` uses the **same** `(bytes, plan)` tuple ([src/domain/retention.py:27-28](src/domain/retention.py:27)) — `__eq__`/`__hash__` fields match, so dict-key/set membership behaves. `__add__` raises `ValueError` on cross-plan and returns a **new** `Retention` ([src/domain/retention.py:6-10](src/domain/retention.py:6)) — does not mutate `self`. Cross-plan combine is `raise ValueError`, not `NotImplemented` — matches the spec key. **Gaps:** `__lt__` at [src/domain/retention.py:20-24](src/domain/retention.py:20) compares only `bytes` and has no cross-plan guard, so `sorted([Retention(10,'A'), Retention(5,'B')])` silently returns a mixed list — spec commentary explicitly requires guarding cross-plan comparison. Also the class is at `src/domain/retention.py`, outside the `src/klip/` package tree — nothing in `klip` imports it, so it is not actually wired into any quota-reporting endpoint (there is no quota endpoint). C10 asked for a value object; it exists as a stub. |
| D1 | PASS | [src/klip/db/session.py:10-15](src/klip/db/session.py:10) | `def get_db():` yields inside `try:` and closes inside `finally:`. Injected via `Depends(get_db)` everywhere: [src/klip/api/deps.py:22](src/klip/api/deps.py:22), all four snippet routes, all five auth routes. |
| D2 | FAIL | grep for `functools`, `wraps`, `@timed`, `timed` returns nothing anywhere under `src/` | There is no timing decorator, no `functools.wraps`, no logging of write-path duration or outcome. Ruled out that a decorator is applied at import time — the import itself is absent. |
| D3 | FAIL | no `seed`, `Seed`, or CLI entry-point matching a seed command in the repo; `[project.scripts]` at [pyproject.toml:25-26](pyproject.toml:25) exposes only `klip = "klip:main"` (which does not exist as a function — [src/klip/__init__.py](src/klip/__init__.py) is empty) | No seed command exists. Streaming vs list is not evaluable because there is nothing that reads a file. |
| D4 | FAIL | same as D3 | No context-manager helper exists because no seed command exists to need one. |
| D5 | FAIL | grep for `retry`, `@retry`, `tenacity` under `src/` returns nothing | No decorator, no external call being decorated. Requirement not attempted. |
| D6 | FAIL | Multiple sites | `ruff check --select B904` reports **2 raises inside an except without `from`**: [src/klip/api/v1/routes_snippet.py:72](src/klip/api/v1/routes_snippet.py:72) and [src/klip/api/v1/routes_snippet.py:75](src/klip/api/v1/routes_snippet.py:75). Independently, the spec requires the internal cause not to reach the client — this is met by `from None` (as the spec key states verbatim). The register/login handlers instead use `from e` **and** put the internal message into the response detail: [src/klip/api/v1/routes_auth.py:31](src/klip/api/v1/routes_auth.py:31) `raise HTTPException(status_code=409, detail=str(e)) from e` and [src/klip/api/v1/routes_auth.py:41](src/klip/api/v1/routes_auth.py:41) `raise HTTPException(status_code=401, detail=str(e)) from e` — both surface the raw `ValueError` message ("Email already exist" / "Invalid credentials") as the client-facing detail and keep the internal traceback chained. Correct uses do exist ([src/klip/api/deps.py:27](src/klip/api/deps.py:27) and neighbours use `from None`; [src/klip/api/v1/routes_snippet.py:44](src/klip/api/v1/routes_snippet.py:44) and :59 use `from e`) — but the requirement is uniform, and it is not uniform. |

---

## 4. Defects found

### SECURITY

**S-1 — 409 handler on registration echoes the internal exception message.**  
[src/klip/api/v1/routes_auth.py:31](src/klip/api/v1/routes_auth.py:31) uses `detail=str(e)` where `e` is a `ValueError("Email already exist")` from [src/klip/services/user_service.py:26](src/klip/services/user_service.py:26). The client sees the raw internal message, which is enough to confirm email existence — an enumeration oracle for anyone probing the registration endpoint. Same shape at [src/klip/api/v1/routes_auth.py:41](src/klip/api/v1/routes_auth.py:41) for `login` (though "Invalid credentials" is already a fixed string there).

**S-2 — No unique constraint on `User.email`.**  
[src/klip/models/user.py:21](src/klip/models/user.py:21) and [migrations/versions/48a9ebaf1d82_user_table.py:26](migrations/versions/48a9ebaf1d82_user_table.py:26) declare `email` with `nullable=False` and no `unique=True`/`UniqueConstraint`. The B2 duplicate check ([src/klip/services/user_service.py:21-26](src/klip/services/user_service.py:21)) is a read-then-write race: two concurrent registrations for the same email both pass the pre-check and both `INSERT`. Two accounts with identical email — authentication then binds a session to whichever row `SELECT` returns first.

**S-3 — `.env` in the working tree contains a real `SECRETKEY`.**  
`.env` is git-ignored (`git check-ignore -v .env` matches the parent repo's `.gitignore:3`), and `git log --all -- .env` returns nothing — never committed. So this is not a public leak, but the file is on-disk in cleartext with a 32-byte hex `SECRETKEY`, a Postgres password, and a database URL that embeds the password. Not a bug, but the value is live and worth rotating if it was ever pasted elsewhere.

### CORRECTNESS

**C-1 — `fetch_snippet` crashes on any snippet without an `expires_at`.**  
[src/klip/services/snippet_service.py:45](src/klip/services/snippet_service.py:45) compares `snippet.expires_at < datetime.now(UTC)` before checking whether `expires_at` is `NULL`. For the entire "no expiry" case — which the schema explicitly permits ([src/klip/models/snippet.py:34](src/klip/models/snippet.py:34) `nullable=True`, [src/klip/schemas/snippet.py:13](src/klip/schemas/snippet.py:13) `expires_at: datetime | None = None`) — this raises `TypeError` and returns a 500 to the client. In production, every `GET /snippet/fetch/{id}` for a persistent snippet is broken.

**C-2 — Empty snippet list returns 404 instead of an empty page.**  
[src/klip/services/snippet_service.py:89-90](src/klip/services/snippet_service.py:89) raises `SnippetNotFound` when the caller has no snippets; [src/klip/api/v1/routes_snippet.py:58-59](src/klip/api/v1/routes_snippet.py:58) turns that into a 404. The first page of a new user's list and the "we ran off the end of the cursor" case both produce 404, which any client written against the spec will treat as a broken endpoint. Additionally, since `limit` is `limit(limit + 1)` at [src/klip/services/snippet_service.py:75](src/klip/services/snippet_service.py:75), a page that is exactly `limit` results also 404s if it happens to be the last page.

**C-3 — `refresh_access_token` timestamp comparison against a naive value.**  
[src/klip/services/auth_service.py:63](src/klip/services/auth_service.py:63) compares `token_row.expire_at < datetime.now(UTC)`. `expire_at` on the model is `DateTime(timezone=True)`, so this is fine when the row was written by this app (login writes an aware `datetime.now(UTC)`), but if any refresh row is ever inserted from a naive source (a fixture, a psql session, a data migration), the comparison raises `TypeError`. Not currently reachable given the write path, but the class of bug that surfaces the moment the write path grows.

### SILENT-FAILURE

**SF-1 — Delete route's role/ownership branches are dead code.**  
[src/klip/api/v1/routes_snippet.py:71](src/klip/api/v1/routes_snippet.py:71) `if e == SnippetForbidden:` and [src/klip/api/v1/routes_snippet.py:74](src/klip/api/v1/routes_snippet.py:74) `if e == SnippetNotFound:` compare an exception instance to the exception class. Exception classes do not define `__eq__` to accept instances of themselves, so both comparisons fall back to `object.__eq__` and always return `False`. Result: the `except (SnippetForbidden, SnippetNotFound)` block swallows both exceptions without raising anything, the function returns `None`, and the client sees **204 No Content**. In production, an ordinary user deleting someone else's snippet gets a 204 (no delete happens); anyone deleting a non-existent id gets a 204. The delete endpoint reports success for every failure it can see. This is the exact "valid Python, runs without error, produces a wrong result" category the exercise is targeting.

**SF-2 — Even if SF-1 were fixed, both branches would then TypeError on the kwarg name.**  
[src/klip/api/v1/routes_snippet.py:72](src/klip/api/v1/routes_snippet.py:72) `HTTPException(status_code=403, details="Forbidden")` and :75 same — `HTTPException` accepts `detail`, not `details`. As soon as the outer comparison is repaired, both raises would produce a 500. Two bugs on one line, the outer one hiding the inner one.

**SF-3 — `services/__init__.py` shadows `login_user`.**  
[src/klip/services/__init__.py:1](src/klip/services/__init__.py:1) `from .user_service import login_user, register_user` then [src/klip/services/__init__.py:2](src/klip/services/__init__.py:2) `from .auth_service import login_user, refresh_access_token, logout_user` — the second import silently rebinds `login_user` to the `auth_service` implementation. The two implementations are near-duplicates ([src/klip/services/user_service.py:39-64](src/klip/services/user_service.py:39) vs [src/klip/services/auth_service.py:23-48](src/klip/services/auth_service.py:23)), and they diverge in the `expire = timedelta(...) + datetime.now(UTC)` line — currently identical, but any future edit to one leaves the other silently in effect depending on import order. Ruff flags this as F811 in section 2.

**SF-4 — Duplicate `SnippetCreate`/`SnippetRead` definitions with different fields.**  
[src/klip/schemas/user.py:32-46](src/klip/schemas/user.py:32) defines `SnippetCreate` and `SnippetRead` **again**, next to the "correct" definitions in [src/klip/schemas/snippet.py](src/klip/schemas/snippet.py). The `user.py` `SnippetRead` is missing `public_id` and missing `model_config = ConfigDict(from_attributes=True)`. `schemas/__init__.py` currently imports the snippet-module versions, so the user-module versions are dead — but a future edit to `schemas/__init__.py` that swaps import order would produce a response model with no `public_id` and no ORM attribute loading, and no test would fail on import.

**SF-5 — `require_admin` dependency is unusable as declared.**  
[src/klip/api/deps.py:49](src/klip/api/deps.py:49) `def require_admin(current_user: User):` has no `Depends(get_current_user)` on the parameter. If a route were to write `Depends(require_admin)`, FastAPI would try to resolve `current_user` as a request parameter (User type is not a recognised body/query type) and return a 500 on every call. The function is currently imported by [src/klip/api/v1/routes_auth.py:6](src/klip/api/v1/routes_auth.py:6) but never used — which is what stops this from breaking anything today.

**SF-6 — `get_current_user` catches `TypeError`, not `ValueError`, when converting the JWT `sub` to UUID.**  
[src/klip/api/deps.py:37-39](src/klip/api/deps.py:37) — `uuid.UUID(user_id)` raises `ValueError` on a malformed string, not `TypeError`. A token whose `sub` is a valid-JWT-but-not-a-UUID string will produce an unhandled `ValueError` → 500 instead of the intended 401. `TypeError` would fire only if `user_id` were, say, a number, which the earlier `is None` check does not rule out but which is not what a bad UUID looks like.

### HYGIENE

**H-1 — `A3` `/health` returns a set, not a dict.**  
[src/klip/main.py:14](src/klip/main.py:14) `return {"Status : okay"}` is a **set literal** with one string element (the `:` is inside the string, so no colon at the top level → not a dict). FastAPI serialises it as `["Status : okay"]`. Almost certainly meant `{"Status": "okay"}`. The requirement is met by luck.

**H-2 — Typo `create_at` on the refresh_tokens table.**  
[src/klip/models/refresh_token.py:20](src/klip/models/refresh_token.py:20) and [migrations/versions/8c0bfa168e54_refresh_token_table.py:30](migrations/versions/8c0bfa168e54_refresh_token_table.py:30) — should be `created_at`. Now baked into the schema; renaming requires another migration.

**H-3 — `noqa` typos don't suppress the rule they name.**  
[src/klip/models/user.py:12](src/klip/models/user.py:12) has `# noqa : UP042` (space before colon), and several `__init__.py` files use `# noqa : F401`. Ruff accepts these lax forms sometimes and not others — [src/klip/models/user.py:12](src/klip/models/user.py:12) still surfaces `UP042` in section 2's ruff run, meaning the suppression did not take effect there.

**H-4 — `SnippetTable.public_id` is not `unique=True`.**  
[src/klip/models/snippet.py:25](src/klip/models/snippet.py:25) — the column is `index=True` but not unique, and the migration index at [migrations/versions/30f84b793702_snippet_table_public_key_added.py:25](migrations/versions/30f84b793702_snippet_table_public_key_added.py:25) is `unique=False`. Collisions at 32 URL-safe bytes are astronomically unlikely but the DB does not enforce the invariant that the app relies on for the shareable link.

**H-5 — `access_token_expires` unit mismatch.**  
[src/klip/core/security.py:27](src/klip/core/security.py:27) reads `access_token_expires` as **minutes**; [src/klip/services/auth_service.py:37](src/klip/services/auth_service.py:37) and :75 use `refresh_token_expires` as **days**. The `.env` values (15 and 30) are compatible with those units, but there is no naming convention to prevent someone reading them as the same unit next time.

**H-6 — Empty `.env.example`.**  
`.env.example` exists but has zero bytes ([$ ls -la .env.example](.env.example)). It is in git; a new checkout has no template of what to put in `.env`, which is exactly what the file is for.

**H-7 — `src/klip/__init__.py` is empty but `[project.scripts]` points at `klip:main`.**  
[pyproject.toml:26](pyproject.toml:26) exposes `klip = "klip:main"`. There is no `main` in [src/klip/__init__.py](src/klip/__init__.py) (empty file), so `pip install .` followed by `klip` on the command line raises `AttributeError: module 'klip' has no attribute 'main'`. Not runtime-reachable through uvicorn, but broken as a distribution.

---

## 5. Security review

Commands run:
- `git log -p -- .env` (across the whole `backend-labs/` repo): no output; `.env` has never been committed.
- `git check-ignore -v .env`: `.gitignore:3` matches → `.env` is ignored.
- `git ls-files | grep -E "\\.env|__pycache__|\\.pyc$"`: only `.env.example` (a zero-byte template) is tracked. No `__pycache__` and no `.pyc` in the index.

Findings that are security-shaped rather than correctness-shaped, referenced from section 4:

- **S-1** and **B2 partial**: registration handler echoes internal `ValueError` messages to the client, giving an email-enumeration oracle. [src/klip/api/v1/routes_auth.py:31](src/klip/api/v1/routes_auth.py:31).
- **S-2**: `User.email` has no DB uniqueness — a race between two registrations for the same email produces two accounts, undermining the "one account per email" security assumption.
- **S-3**: `.env` present on disk with a real `SECRETKEY`, DB password embedded in `DATABASE_URL`; not committed, not leaked as far as this audit can see, but flagged so the value can be rotated if it has ever been shared.
- **B8 FAIL**: no working authorisation dependency for the privileged role. The dependency that exists ([src/klip/api/deps.py:49-54](src/klip/api/deps.py:49)) is imported by [src/klip/api/v1/routes_auth.py:6](src/klip/api/v1/routes_auth.py:6) but referenced by no route; the actual role check is inline in `snippet_service.delete_snippet`, which is exactly what B8 said not to do.
- **C7 side channel** (informational): fetch-snippet timing between "never existed" and "private-not-yours" differs by no DB round-trip in the current implementation (both do a single `SELECT`), so this is not exploitable today, but the spec's own commentary asks that this be understood.
- **SF-1**: the DELETE endpoint returns 204 (success) for both "not your snippet" and "does not exist". Callers who trust the status code will believe deletes succeeded when nothing happened.
- **`get_current_user`** does no `algorithms=` mismatch check beyond what PyJWT enforces from the token; it does honour the `settings.secretkey` and `algorithms=["HS256"]` at [src/klip/core/security.py:34](src/klip/core/security.py:34) — good.
- No route logs the raw refresh token or password anywhere I could find; searches for `logger`, `print(`, `logging.` under `src/` return nothing (no logging at all — see D2).
- No credentials appear in URLs or query parameters; login uses form body, refresh takes the token in the JSON body.

---

## 6. Runtime checks the author must run

Numbered, matching the verification checklist in the spec. Each names the exact endpoint / input / observation that would count as a pass.

**Foundations**

1. `docker compose up -d db` from the repo root → `docker compose ps` shows the `klip-db-1` container `healthy`; `psql -h localhost -p 5435 -U klip -d klip_db` connects. **Pass = connect succeeds on port 5435.**
2. `docker compose down` (keep the volume) then `docker compose up -d db` again → an existing table's row from the previous session is still there. **Pass = the row is present.**
3. `unset DATABASE_URL` (or comment it out in `.env`) and start the app → the process must **exit at import time** with a `pydantic_settings.ValidationError` that names `database_url`. **Pass = the error message includes the field name; a 500 at first request is a FAIL.** Note the A2 partial: run this from a directory other than the repo root too — the current `env_file=".env"` is relative, so the failure mode may be "everything missing" rather than "the specific field you unset".
4. Set `ACCESS_TOKEN_EXPIRES=notanumber` in `.env` → same behaviour, and the error must name `int` (or `access_token_expires`). **Pass = the process refuses to start and the error names the type.**
5. `curl -i http://localhost:8000/health` → HTTP 200, body `["Status : okay"]` (see H-1). **Pass = 200 status.**
6. `alembic upgrade head` then `psql … -c "\d User" -c "\d snippets" -c "\d refresh_tokens"` → all three tables visible with the columns and types shown in the migrations. **Pass = all three exist with the expected columns.**
7. `alembic downgrade -1` then `alembic upgrade head` → succeeds without error and `psql -c "SELECT * FROM alembic_version"` shows the head revision `9fc79e201f55`. **Pass = the head revision is the latest.**
8. `.venv/bin/ruff check src/` → currently **exits 1 with 33 errors**. **Pass = exit 0. Current state = FAIL.**

**Accounts**

9. `POST /auth/register` with `{"email":"a@b.c","password":"pw"}` → 201, response is a `UserRead` without a password field; `psql -c "SELECT hashed_password FROM \"User\" WHERE email='a@b.c'"` shows a string beginning with `$argon2id$`. **Pass = 201 + argon2 hash in DB, and the response JSON has no `hashed_password`/`password` key.**
10. Register two users with the same password → the two `hashed_password` values in `psql` are **different strings**. **Pass = distinct hashes.**
11. Register the same email twice → the second call returns **409** (currently with `detail="Email already exist"` — see S-1). **Pass = 409 status.**
12. `POST /auth/login` (form-encoded `username=…&password=…`) → 200, body has `access_token`, `refresh_token`, `token_type: "bearer"`. **Pass = both tokens present.**
13. Paste the `access_token` into jwt.io — header `alg: HS256`, payload has `sub` (a UUID) and `exp` (a unix timestamp roughly `now + settings.access_token_expires * 60`). **Pass = `exp` is within a few seconds of that value.**
14. `POST /auth/refresh` with `{"refresh_token": "<the one you got at login>"}` → 200 with a **new pair**. **Pass = the new `refresh_token` differs from the old one.**
15. Immediately `POST /auth/refresh` again with the **same original** refresh token → 401 (`credential_exception`). **Pass = 401. If a 200 is returned, B4 has regressed.**
16. `psql -c "SELECT hashed_token FROM refresh_tokens ORDER BY create_at DESC LIMIT 1"` → the stored value is a **64-char hex string** and does **not** equal the raw `refresh_token` the client holds. **Pass = client value and DB value differ, and the DB value looks like SHA-256 hex.**
17. `POST /auth/logout` with a valid refresh token → 204. Immediately try refresh with the same token → 401. **Pass = second call is 401.**
18. `POST /auth/logout` with `{"refresh_token": "garbage"}` → **204**, same status as (17). **Pass = 204 in both cases, with no difference in body.**
19. `GET /auth/me` with a valid `Authorization: Bearer <access>` → 200, JSON has `id`, `email`, `role`, and **no** `hashed_password` or `password`. **Pass = only those three keys.**
20. `GET /auth/me` with no `Authorization` header → 401 with `WWW-Authenticate: Bearer`. **Pass = 401.**
21. `GET /auth/me` with an expired `access_token` (wait `access_token_expires` minutes, or manually craft one) → 401. **Pass = 401.**
22. Admin path: promote a user to `PRIVILEGED` in `psql` (`UPDATE "User" SET role='PRIVILEGED' WHERE email='admin@x'`) and have them `DELETE /snippet/{public_id}` for a snippet owned by someone else. **Currently returns 204 but only because SF-1 makes every response 204** — you must verify **the row is actually gone** in `psql` (`SELECT * FROM snippets WHERE public_id=…`), not just the status code. **Pass = row deleted.**
23. Same delete but from an ordinary (non-owner, non-privileged) account → currently returns 204 and does not delete the row (SF-1). **Expected pass = 404 (matching C7); actual = 204 and row still present. This is a FAIL to record.**

**Snippets**

24. `POST /snippet` with `{"title":"t","body":"b","visibility":"public"}` and a valid token → 201; `psql -c "SELECT id, public_id, visibility FROM snippets"` shows the row. **Pass = row present.**
25. `psql -c "INSERT INTO snippets (id, owner_id, public_id, body, title, visibility) VALUES (gen_random_uuid(), '<a real user id>', 'x', '', 't', 'BOGUS')"` → **error from Postgres** `invalid input value for enum visiblevalue: "BOGUS"`. **Pass = the INSERT fails at the DB.** Note per row C2: the enum stores the uppercase names (`PUBLIC`, `UNLISTED`, `PRIVATE`), so the valid strings for a raw `INSERT` are the uppercase forms; lowercase `'public'` is also rejected by the DB (the app inserts the uppercase via the ORM).
26. Create a snippet and inspect its row in `psql` → `created_at` is populated; there is no `Column.default=datetime.now(...)` on this column in the model. **Pass = the row has a non-null `created_at` even though the Python code never sets it.**
27. Create three snippets and compare their `public_id` values → they are 43-character URL-safe base64 strings (`secrets.token_urlsafe(32)`) with no visible ordering. **Pass = they are not sequential and each is ~43 chars.**
28. `POST /snippet` with an extra `owner_id` in the body pointing at another user → the snippet is still created with `owner_id = your_own_id`. **Pass = the extra field is ignored and the row's `owner_id` matches the logged-in user.**
29. All four C6 cases: create a public, an unlisted (share the id), a private (owned by you), and an expired (set `expires_at` in the past). **You must set `expires_at` on all four** (see C-1) or the non-expired ones will 500 rather than 404/200. Then:
    - public → `GET /snippet/fetch/{id}` with **no** auth → 200
    - unlisted → same → 200
    - private (yours) with your auth → 200
    - private (yours) with another user's auth → 404 (see step 30)
    - expired → 404 (see step 30)  
    **Pass = the four rows above.** If any GET produces 500 instead of a 404/200, C-1 is what you hit — the row has no `expires_at`.
30. Byte-compare responses for three requests: private-not-yours, expired, never-existed (a random 43-char `public_id`). Use `curl -is … | tail -c 200` on all three and `diff`. **Pass = the three response bodies and status lines are identical byte-for-byte.** They currently are, at [src/klip/api/v1/routes_snippet.py:43-44](src/klip/api/v1/routes_snippet.py:43).
31. `GET /snippet/snippetlist` while logged in as a user with only their own snippets → newest first. Create a second user, log in as them, `GET` again → only the second user's snippets returned. **Pass = no leakage across users.** Note C-2: **if the second user has zero snippets, this returns 404 rather than an empty page** — that is the bug, not a passing test.
32. `GET /snippet/snippetlist?limit=99999` → **422** (from the `le=settings.max_page_size` on the `Query`), not honoured. **Pass = 422.**
33. Load `Retention` in a REPL (`python -c "from domain.retention import Retention; …"` after adding `src/` to `PYTHONPATH`) and exercise: `Retention(100,'A') == Retention(100,'A')` → True; `{Retention(100,'A'): 1}` uses it as a key; `sorted([Retention(5,'A'), Retention(10,'A')])` returns them in ascending order; `Retention(100,'A') + Retention(50,'A')` returns `Retention(150,'A')` **without mutating** either input. **Pass = all four behaviours as described.**
34. `Retention(1,'A') + Retention(1,'B')` → raises `ValueError("Cannot combine different plans")`. **Pass = raises.** Also try `sorted([Retention(1,'A'), Retention(2,'B')])` — currently sorts silently (see C10 note); **expected pass = raises; actual = silent, a spec gap to note**.

**Plumbing**

35. Add a temporary route that raises inside the try/finally of a session dependency (or force a 500 on an existing route) and, before/after, observe `SELECT count(*) FROM pg_stat_activity WHERE datname='klip_db'` → the count does not grow. **Pass = the count is stable after N raising requests.**
36. Any of the write endpoints — `POST /snippet`, `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `DELETE /snippet/{id}` — should produce a log line with duration and outcome. **Pass = the log line exists and shows the real function name (`create_snippet`, `register_user`, …), not `wrapper`. Current state = FAIL, no logging exists at all (D2).**
37. Same as 36 — verify the logged function names are the real ones. **Current state = N/A because no logging is emitted.**
38. Point a seed command at a 1GB JSONL file and watch `ps -o rss=` for the process → RSS stays flat. **Current state = FAIL, no seed command exists (D3).**
39. Point a seed command at a JSONL file with a broken line in the middle → the file handle is closed (check with `lsof -p <pid> | grep <path>` after the failure). **Current state = FAIL, no seed command exists (D4).**
40. Point a `@retry(times=3)`-decorated call at a mocked failing service → three attempts logged, then failure. **Current state = FAIL, no retry decorator exists (D5).**
41. Trigger a client-facing error whose cause is an internal exception (e.g. a DB IntegrityError bubbling up through `register`) → the response body does not contain any internal detail (no `IntegrityError`, no traceback). **Currently the register/login handlers put `str(e)` into `detail` — the internal message *is* in the response.** Pass = the response `detail` is a fixed sanitised string; current state = FAIL for the register/login paths.

---

## 7. Git and process audit

- `git log --oneline` (whole `backend-labs/` repo — the `.git` directory is at the parent, not at `challenges/klip/`) → **16 commits**. Subjects are descriptive and none look like a branch slug. There is one minor spelling weakness — "Add snippets model, schema and endpoints" is fine; "Keep correct implementation of retry" is odd English but describes a change. No `fixup!` / `WIP` / squash artifacts. No merge subjects either.
- `git branch -a` → `main` locally, `remotes/origin/HEAD → origin/main`, `remotes/origin/main`. **No other branches.** Combined with the log, this means no feature-branch or PR workflow was used for Klip — every change was pushed straight onto `main`. The spec explicitly asked for **four PRs, one per section, squash-merged**, and none of that happened.
- `git log --merges --oneline | wc -l` → **0 merge commits**. All 16 are direct commits on `main` (i.e. everything is effectively squashed by virtue of never having been on a branch).
- `.env` is ignored: `git check-ignore -v .env` → matches `.gitignore:3`. **Not committed** (verified with `git log -p -- .env` returning nothing).
- `__pycache__` is ignored: `git check-ignore -v src/klip/__pycache__` → matches `.gitignore:2`. `git ls-files | grep __pycache__` returns nothing. **Not committed.**
- Files that arguably should not be committed: `.env.example` is committed but is zero bytes (H-6). `.ruff_cache/` sits in the working tree at [.ruff_cache](.ruff_cache) — quick check: `git ls-files | grep ruff_cache` returns nothing, so it's untracked, and it should be added to `.gitignore` explicitly.

---

## 8. Grade

Per-section arithmetic, with `PASS=1.0, PARTIAL=0.5, FAIL=0, NOT STATICALLY VERIFIABLE=excluded`.

**Section A** (weight 15%)  
A1=1 · A2=0.5 · A3=1 · A4=1 · A5=1 · A6=0 → 4.5 / 6 = **0.750**

**Section B** (weight 35%)  
B1=1 · B2=0.5 · B3=1 · B4=1 · B5=1 · B6=1 · B7=1 · B8=0 → 6.5 / 8 = **0.813**

**Section C** (weight 30%)  
C1=1 · C2=1 · C3=1 · C4=1 · C5=1 · C6=0.5 · C7=1 · C8=0.5 · C9=0 · C10=0.5 → 7.5 / 10 = **0.750**

**Section D** (weight 20%)  
D1=1 · D2=0 · D3=0 · D4=0 · D5=0 · D6=0 → 1 / 6 = **0.167**

**Overall** = 0.15·0.750 + 0.35·0.813 + 0.30·0.750 + 0.20·0.167  
= 0.1125 + 0.2844 + 0.2250 + 0.0333  
= **0.6552 → 66%**

Zero requirements were marked NOT STATICALLY VERIFIABLE — every verdict is grounded in a code cite.

**Verdict.** Sections A, B, and C are largely there — Klip is a functioning enough shape that the happy paths work. The grade is dragged down by Section D, where five of the six requirements were not attempted at all: no timing decorator, no seed command, no context-manager helper for the seed, no retry, and D6 is broken in two ways (two raises without `from` at [src/klip/api/v1/routes_snippet.py:72](src/klip/api/v1/routes_snippet.py:72) and :75, and the register/login handlers echo internal `ValueError` messages back to the client at [src/klip/api/v1/routes_auth.py:31](src/klip/api/v1/routes_auth.py:31) and :41). Within B and C, the two failures worth internalising are (a) B8 — the `require_admin` dependency exists at [src/klip/api/deps.py:49-54](src/klip/api/deps.py:49), is imported into `routes_auth.py`, is not called by anything, and is also structurally broken (no `Depends(get_current_user)` on the parameter); the actual role check ended up inline in `snippet_service.delete_snippet` at [src/klip/services/snippet_service.py:114-119](src/klip/services/snippet_service.py:114), which is exactly what the requirement said not to do — and (b) C9/SF-1, where `if e == SnippetForbidden:` at [src/klip/api/v1/routes_snippet.py:71](src/klip/api/v1/routes_snippet.py:71) and :74 compares instance to class, both branches are always False, both branches are dead, the delete endpoint returns **204 for every failure mode** (non-owner, not found), and the second bug hiding behind the first is that the kwarg is `details` (not `detail`) — so even fixing the outer comparison would still 500 on the raise. That single method is the cleanest example in the exercise of a silent-failure defect. What is strong: B4/B5 on refresh-token rotation are correct — one commit does revoke-and-issue at [src/klip/services/auth_service.py:70-78](src/klip/services/auth_service.py:70) with SHA-256 at rest at [src/klip/core/security.py:43-44](src/klip/core/security.py:43); C7 is met exactly at [src/klip/api/v1/routes_snippet.py:43-44](src/klip/api/v1/routes_snippet.py:43); A5 and C2 use the database in the way the spec asked, not just the ORM.

---

## 9. What I could not determine

- Every runtime observation in section 6 is by definition not statically verifiable — the spec is explicit that "nothing is done on your word." Those items are listed there rather than left as verdict gaps.
- A2 is marked PARTIAL rather than FAIL on the assumption that "required setting has no default" is the primary bar and "relative `env_file`" is a secondary miss; the spec's key wording (`env_file` "absolute or `__file__`-anchored") suggests the miss is real but does not invalidate the fail-fast property, hence 0.5 rather than 0.
- C7 is marked PASS on the strength of the response being byte-identical for the three cases the fetch endpoint handles ([src/klip/api/v1/routes_snippet.py:43-44](src/klip/api/v1/routes_snippet.py:43)). C9 asks the delete endpoint to also treat non-owner as indistinguishable-from-not-found — I graded that as a separate FAIL on C9 rather than reducing C7, because the C7 line item is specifically about the fetch behaviour.
- C10's `__lt__` cross-plan guard is missing but same-plan sorting works and dict-key/set membership works. I treated that as PARTIAL rather than FAIL because the spec's line-item text (`__eq__`/`__hash__`/`__add__`/sortable/error-not-guess) is satisfied except for the cross-plan-comparison detail that only appears in the spec commentary; a stricter reading would push it to FAIL.
- D6 uses `from e` in several places where the spec key text uses `from None`. I have graded that as part of the FAIL (combined with the two `raise …` without any `from` at all and the `detail=str(e)` leaks). A more lenient reading — "any `from` counts" — would move D6 to PARTIAL and the overall to ~67%.
- Whether the challenge's "package structure" A4 was intended to include `src/domain/retention.py` under `src/klip/` — the current layout has `Retention` outside the `klip` package. I graded A4 as PASS (the `klip` package itself is structured as required) and noted the placement separately under C10.
- The whole audit ignores tests because there are none: `find . -path ./.venv -prune -o -name "test_*.py" -print -o -name "*_test.py" -print` returns nothing. If any of the verdicts above are meant to be self-verified, none of that verification exists as automated tests either.
