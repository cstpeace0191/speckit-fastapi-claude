# Research: To-Do List Web App

**Date**: 2026-11-14 | **Plan**: [plan.md](plan.md)

No `NEEDS CLARIFICATION` items remain: the stack is fixed by the existing code and the spec's
clarifications are resolved. The decisions below cover the gaps found when comparing the spec with
the existing code.

## R1. Rename mechanism (Clarification Q1: C)

- **Decision**: A separate edit button per item opens a `react-bootstrap` `Modal` with a labelled
  text input prefilled with the current name. Save calls the existing `PUT /api/items/{id}` with
  `name`. Cancel closes the dialog. Focus returns to the edit button when it closes.
- **Rationale**: Matches the clarified choice. `PUT` already accepts partial updates (FR-005), so
  no new endpoint is needed. `Modal` is already in the dependency tree, so no new package is added.
- **Alternatives considered**:
  - Inline editing on the name (rejected in Q1: option B). Clicking the name would conflict with
    the checkbox and trash targets and is harder to make keyboard-accessible.
  - A new `PATCH` endpoint (rejected). It would duplicate `PUT` behavior with no benefit.

## R2. Oldest-first ordering needs a stored creation order (Clarification Q3: A)

- **Decision**: Add a `created_seq` column to `todo_items`:
  - **SQLite**: `created_seq INTEGER`. On insert, set it to `COALESCE(MAX(created_seq), 0) + 1`
    within the same statement. Backfill existing rows with `rowid` on migration. Query with
    `ORDER BY created_seq`.
  - **MySQL**: `created_seq BIGINT AUTO_INCREMENT UNIQUE` added by `ALTER TABLE` if missing. The
    database assigns it on insert. Query with `ORDER BY created_seq`.
- **Migration**: Both backends check for the column at startup and add it only if absent, so
  existing data survives (FR-009). `CREATE TABLE IF NOT EXISTS` alone would not add the column to
  an existing table, so the check is required.
- **Rationale**: The current table has no creation time or sequence. SQLite `rowid` is not used as
  the order key because `VACUUM` may renumber rows in tables without an `INTEGER PRIMARY KEY`.
  An explicit column is stable across both backends.
- **Alternatives considered**:
  - Order by a stored timestamp. Rejected: two items added in the same millisecond have no defined
    order, and the spec requires a strict insertion order.
  - Order by `rowid` alone. Rejected for the `VACUUM` reason above.
  - Recreate the table. Rejected: more risk to existing data than an additive `ALTER`.
- **Known limit**: Existing rows in MySQL receive `created_seq` values in the database's current
  row order, which may not match their original creation order. This is acceptable because no
  creation order was ever recorded for them.

## R3. Name validation placed in the model layer

- **Decision**: In `models.py`, `ItemCreate` and `ItemUpdate` strip surrounding whitespace, then
  require 1 to 255 characters. Input that is empty after stripping returns 422. The stored name is
  the trimmed value.
- **Rationale**: One validation point covers both add (FR-003, FR-004) and rename (FR-014). It
  returns the standard 422 response that the existing client already handles. Trimming matches the
  spec's rule that space-only names count as empty.
- **Alternatives considered**:
  - Validate only in the client. Rejected: the server must enforce rules itself, and the API
    accepts other callers.
  - Store untrimmed names. Rejected: the spec says space-only is empty, and trimming keeps
    "Buy milk " and "Buy milk" from looking different.

## R4. Missing-item handling on delete (FR-011)

- **Decision**: `DELETE /api/items/{id}` first looks up the item and returns 404
  `"Item not found"` if it is missing. The client treats 404 on any action as "item no longer
  exists", shows a message, and reloads the list.
- **Rationale**: The current delete returns 200 even when nothing was deleted, so the client cannot
  tell that the item is gone. `PUT` already returns 404, so this makes delete consistent with it.
- **Alternatives considered**: Keep 200 and rely on the client refresh. Rejected: it hides the
  message the spec requires.

## R5. Client error states (FR-011, FR-012)

- **Decision**:
  - A load failure sets a separate `loadError` state. It shows an alert with a "Try again" button,
    never the empty-state message.
  - Add, toggle, rename, and delete failures show an alert in a shared `aria-live="polite"` region.
  - The client updates item state from mutation responses (constitution IV) and uses functional
    `setItems` updates to avoid stale closures.
- **Rationale**: The current code turns a failed load into `[]`, which falsely shows "No items yet!"
  (spec Edge Case 3). Failed mutations only log to the console, so the user sees nothing.
- **Alternatives considered**: A global toast library. Rejected: it would add a dependency for a
  single live region.

## R6. Test coverage for the client

- **Decision**: Backend changes follow test-first with pytest (constitution II). Client changes are
  verified by `npm run lint`, `npm run build`, and the manual steps in `quickstart.md`, which map
  to the spec's acceptance scenarios.
- **Rationale**: The client has no unit-test framework. Adding one (for example Vitest with React
  Testing Library) would add dependencies and setup that are outside this feature.
- **Follow-up**: Adding a client test framework is a candidate for a separate feature. Until then,
  UI acceptance rests on the manual checks.

## R7. Accessibility details

- **Decision**:
  - Remove button: `aria-label="Remove {name}"`.
  - Toggle button: keep the existing state-aware label, plus the item name.
  - Add button disabled when the trimmed input is empty (spec FR-005).
  - Input `maxLength={255}` so the limit is visible while typing.
  - Completion is conveyed by icon and by text, not color alone (constitution III).
- **Rationale**: Each control states its action and its item, as the constitution requires.

## R8. Declared dependencies (constitution I)

- **Decision**: Add `prop-types` to `client/package.json` `dependencies`, at the version already
  installed transitively, so the import is declared.
- **Rationale**: The constitution forbids relying on transitive dependencies, and the requirements
  note in `requirement-KR.txt` §10 records this as a known gap.
