<!--
SYNC IMPACT REPORT (temporary; remove before committing)
Version change: 1.0.0 → 2.0.0 (MAJOR: Principle II narrowed; regression tests now required for
backend bug fixes only, and client bug fixes use manual checks until a client test framework exists)
Principle count: template defines 5 slots; user requested 4 → 4 principles adopted.
Modified principles: none (initial adoption). Template slots mapped as:
  PRINCIPLE_1 → I. Code Quality
  PRINCIPLE_2 → II. Test-First (NON-NEGOTIABLE)
  PRINCIPLE_3 → III. Accessibility
  PRINCIPLE_4 → IV. Performance
  PRINCIPLE_5 → removed (not requested)
Added sections: Additional Constraints (SECTION_2), Development Workflow (SECTION_3).
Removed sections: none.
Deferred TODOs:
  - TODO(PERF_BUDGET): numeric latency budget not yet measured.
  - TODO(CORS_PROD): production CORS origin list not defined (NFR-02 allows all origins).
  - TODO(LINTER_BACKEND): no Python linter/formatter is configured for backend/.
  - TODO(A11Y_TOOLING): no automated a11y linter (e.g., eslint-plugin-jsx-a11y) is configured.
Assumption: RATIFICATION_DATE set to 2026-11-14 (first adoption; confirm if an earlier date applies).
-->

# getting-started-todo-app-FastAPI Constitution

## Core Principles

### I. Code Quality

- Client code MUST pass `npm run lint` (ESLint, `client/.eslintrc.cjs`) and MUST be formatted
  with Prettier before merge.
- Backend Python code MUST annotate all public functions and MUST use Pydantic models for every
  request and response body (as in `backend/src/models.py`).
- Route handlers in `backend/src/routes/` MUST NOT contain SQL or driver calls; all persistence
  MUST go through `backend/src/persistence/`.
- Commented-out code, unused imports, and dead code MUST NOT be merged.
- Every runtime import MUST be declared in `backend/requirements.txt` or `client/package.json`.
  Relying on a transitive dependency (for example `prop-types`) is NOT permitted.

Rationale: the SQLite and MySQL backends are swapped by environment variables. Layering and
explicit dependencies keep that swap safe and keep the codebase reviewable.

### II. Test-First (NON-NEGOTIABLE)

- Each new or changed API endpoint and each persistence operation MUST have a pytest test in
  `backend/spec/` that is written first and observed to fail before the implementation is added.
- Every backend bug fix MUST include a pytest regression test that fails before the fix and
  passes after it. Client bug fixes are verified by the manual checks in
  `specs/001-todo-list-app/quickstart.md`, and the pull request MUST list the checks run. A client
  test framework MAY be adopted through a separate feature.
- The Docker `test` stage MUST pass before the `final` image is built (NFR-04).
- Tests MUST NOT require a running MySQL server or share state. SQLite tests MUST use a temporary
  database path per test.

Rationale: the Docker build already gates on tests, so a test that is written late gives no
protection against regressions in the image.

### III. Accessibility

- Every interactive control (completion toggle, delete, add-item form) MUST be operable with the
  keyboard alone and MUST show a visible focus indicator.
- Icon-only controls in `client/src/components/ItemDisplay.jsx` MUST have an accessible name
  (for example `aria-label`) that states the action and the item.
- Inputs in `AddNewItemForm.jsx` MUST have an associated label. The disabled state of the submit
  button MUST be exposed to assistive technology, not conveyed by color alone.
- Completion state MUST NOT be conveyed by color alone. It MUST also be shown by the checkbox icon
  or by text.
- Text and interactive controls MUST meet WCAG 2.1 AA contrast (4.5:1 for normal text).
- The empty-state message ("No items yet! Add one above!", FR-02) MUST be rendered as text.
- Adding, deleting, or toggling an item SHOULD be announced through an `aria-live` region, because
  the change is otherwise silent to screen-reader users.

Rationale: the application is a small, single-purpose UI, so each control is on the critical path
for every user.

### IV. Performance

- All database I/O MUST be asynchronous (aiosqlite / aiomysql, NFR-01). Blocking calls inside
  request handlers are prohibited.
- The MySQL connection pool bounds (min 1, max 5) MUST NOT be changed unless the pull request
  records a load measurement that justifies the change.
- Each CRUD endpoint MUST meet the latency budget in TODO(PERF_BUDGET). The budget MUST be measured
  on the local SQLite backend before it is enforced.
- Production artifacts MUST be built with `npm run build` (Vite). Development-only packages MUST
  NOT appear in the `final` image.
- The client SHOULD update its local list from the response of a single mutation instead of
  re-fetching the full item list, unless the response does not contain the changed item.

Rationale: the `final` image serves the SPA from FastAPI, so bundle size and backend latency are
both visible to every user.

## Additional Constraints

- Technology stack is fixed by `requirement-KR.txt` §7: Python 3.12, FastAPI, Pydantic v2,
  aiosqlite / aiomysql, Node.js 22, React 19, Vite 6, and React-Bootstrap. Changing a major
  version requires a MINOR amendment of this constitution.
- Data persistence MUST survive restart (FR-07) for both SQLite and MySQL.
- The CORS policy (NFR-02) that allows all origins applies to development only. A production
  origin list MUST be defined before deployment (TODO(CORS_PROD)).
- The MIME-type registration in the backend (NFR-03) MUST be kept for Windows compatibility.
- Credentials in `compose.yaml` are development-only. Production MUST use Docker secrets or
  environment variables.
- Generated folders (`backend/.venv`, `.pytest_cache`, `client/dist`, `backend/src/static`) MUST
  NOT be committed.

## Development Workflow

- Feature work follows the Spec Kit sequence: specify → clarify → plan → tasks → implement.
- Before a change is merged, all of the following MUST pass: `pytest` in `backend/`, `npm run lint`
  and `npm run build` in `client/`, and the Docker `test` stage.
- Code review MUST confirm compliance with each principle above. Any violation MUST either be
  fixed or be justified in the pull request description, with the justification approved by a
  reviewer.

## Governance

- This constitution supersedes all other development practices in this repository.
- Amendments are made by a pull request that edits this file and includes an updated Sync Impact
  Report. The amendment MUST be approved by a project maintainer before merge.
- Versioning follows semantic versioning:
  - MAJOR: a principle is removed or its meaning is reversed.
  - MINOR: a principle or section is added, or existing guidance is materially expanded.
  - PATCH: wording, typo, or clarification changes with no change in meaning.
- Compliance is checked at every pull request review (see Development Workflow). Complexity beyond
  the principles MUST be justified in the pull request description.
- Runtime development guidance is in `README.md`, `workflow.md`, and `backend/README.md`.

**Version**: 2.0.0 | **Ratified**: 2026-11-14 | **Last Amended**: 2026-11-14
