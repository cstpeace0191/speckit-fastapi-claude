# Implementation Plan: To-Do List Web App

**Branch**: `001-todo-list-app` (not a git repository) | **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-todo-list-app/spec.md`, with the existing stack described in `requirement-KR.txt`.

## Summary

The app already exists as a working FastAPI + React to-do list. Its code was copied from
`practices/getting-started-todo-app-FastAPI/` into this repository. It covers the add, list, complete, delete, welcome
message, and restart-persistence behavior. This plan covers the changes needed to meet the
clarified spec, which are not yet in that code:

1. **Rename** through an edit dialog (Clarification Q1, FR-013 to FR-015, Story 6).
2. **Oldest-first order** that stays stable when items are completed (Q3, FR-002). The current
   table has no creation-order column and the list query has no `ORDER BY`, so this needs a schema
   change and migration.
3. **Name rules** for add and rename: at least one non-space character, at most 255 characters,
   stored trimmed (FR-010, FR-014). The current server accepts whitespace-only names and does not
   validate rename.
4. **Honest error states**: a failed load must not show "No items yet!" (FR-012), and failed
   actions must show a message (FR-011). The current client only logs errors to the console and
   turns a failed load into an empty list.
5. **Deleting or changing a missing item** must return 404 and tell the user (FR-011). Delete
   currently returns 200 for missing items.
6. **Accessibility gaps** the constitution requires: the remove button needs an accessible name
   that includes the item, and the disabled Add button must ignore whitespace-only input.

The shared list (Q2) and the 2-second list target (Q4) need no code change beyond what exists.

## Technical Context

**Language/Version**: Python 3.12 (backend); JavaScript on Node.js 22 (client)

**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, aiosqlite, aiomysql (backend);
React 19, Vite 6, React-Bootstrap, Bootstrap 5, FontAwesome (client)

**Storage**: SQLite by default (file path from `SQLITE_DB_LOCATION`); MySQL 9.3 when `MYSQL_HOST`
or `MYSQL_HOST_FILE` is set. One table, `todo_items`.

**Testing**: pytest + pytest-asyncio + httpx `ASGITransport` for the backend (`backend/spec/`).
The client has ESLint and Prettier but no unit-test framework; UI behavior is verified by the
manual steps in `quickstart.md` (see Research R6).

**Target Platform**: Linux containers (Docker Compose, `final` image) and Windows local
development.

**Project Type**: Web application: FastAPI JSON API plus a React single-page app that the same
backend serves as static files.

**Performance Goals**: A list of 100 items appears within 2 seconds (SC-006, confirmed in
clarification). Each CRUD request should be measured on SQLite before a stricter budget is set
(constitution `TODO(PERF_BUDGET)`).

**Constraints**: All database I/O is async (NFR-01). MySQL pool size stays at min 1, max 5
(`requirement-KR.txt` §5; this plan does not change it). WCAG 2.1 AA contrast and keyboard operation (constitution III). No new
runtime dependencies unless declared in `requirements.txt` or `package.json` (constitution I).

**Scale/Scope**: One shared list (Q2). Tested up to 100 items (SC-006). No pagination.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan meets it |
|-----------|--------|------------------------|
| I. Code Quality | Pass, with one required change | Routes keep calling `persistence/` only. Request bodies stay Pydantic models. **Required change:** `prop-types` is imported but not declared in `client/package.json`; add it (constitution I). |
| II. Test-First (NON-NEGOTIABLE) | Pass, with a required order | Every changed endpoint and persistence operation gets a failing pytest test before its code change: ordering, name validation, 404 on delete, migration. The Docker `test` stage gates the `final` image. Client behavior is covered by manual checks (R6). |
| III. Accessibility | Pass, with required changes | Remove button gets an accessible name that includes the item. The rename dialog is keyboard-operable, labelled, and returns focus to its trigger on close. Add button disabled state uses trimmed input. Load and action errors are announced through a polite live region. |
| IV. Performance | Pass | One `SELECT ... ORDER BY` per list request, no N+1 queries. Client updates list state from mutation responses instead of refetching. `PERF_BUDGET` stays open until SQLite is measured. |
| Additional: persistence | Pass | Migration adds the ordering column without dropping data; existing rows are backfilled (R2). |
| Additional: CORS, secrets | Out of scope for this feature | The CORS and credential items in the constitution apply at deployment time. This plan does not change them. |
| Workflow | Pass | Plan includes `pytest`, `npm run lint`, `npm run build`, and the Docker `test` stage as merge gates. |

**Result**: No unjustified violations. Complexity Tracking below stays empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-list-app/
├── spec.md                  # Feature specification (with Clarifications)
├── plan.md                  # This file
├── research.md              # Phase 0: decisions and alternatives
├── data-model.md            # Phase 1: To-Do Item entity and migration
├── quickstart.md            # Phase 1: how to run and verify the feature
├── contracts/
│   └── items-api.md         # Phase 1: HTTP contract for the item endpoints
├── checklists/
│   └── requirements.md      # Spec quality checklist (from /speckit-specify)
└── tasks.md                 # Phase 2 output (/speckit-tasks; not created here)
```

### Source Code (implementation repository)

The application code lives in this Spec Kit repository, at the root (`backend/`, `client/`,
`Dockerfile`, `compose.yaml`). It was copied from `practices/getting-started-todo-app-FastAPI/`,
which is kept as the original. All code paths below are relative to the repository root.

```text
backend/
├── main.py                       # Local entry point (no change expected)
├── requirements.txt              # No new runtime dependency expected
├── src/
│   ├── main.py                   # App factory, lifespan, CORS, static mount (no change)
│   ├── models.py                 # CHANGE: name validation for ItemCreate and ItemUpdate
│   ├── routes/
│   │   └── items.py              # CHANGE: 404 on delete of missing item; ordered list
│   └── persistence/
│       ├── __init__.py           # No change (backend selection)
│       ├── sqlite.py             # CHANGE: created_seq column, migration, ORDER BY
│       └── mysql.py              # CHANGE: created_seq column, migration, ORDER BY
└── spec/
    ├── persistence/test_sqlite.py    # ADD: ordering, migration tests
    └── routes/test_items*.py         # ADD: validation, 404 delete, rename tests

client/
├── package.json                  # CHANGE: declare prop-types
└── src/components/
    ├── TodoListCard.jsx          # CHANGE: separate load-error state; live region; stable updates
    ├── AddNewItemForm.jsx        # CHANGE: trimmed validation; visible error; maxLength 255
    ├── ItemDisplay.jsx           # CHANGE: item-specific labels; rename trigger; visible errors
    ├── RenameItemDialog.jsx      # ADD: react-bootstrap Modal with labelled input
    └── ItemDisplay.scss          # Focus-visible style if needed
```

**Structure Decision**: Keep the existing layered layout (routes → persistence; components →
fetch). Add one component (`RenameItemDialog.jsx`) and no new folders or runtime dependencies.
Rename uses the `Modal` already available in `react-bootstrap`.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

No violations. The schema change (R2) is the only structural change and is required by the
clarified ordering rule.
