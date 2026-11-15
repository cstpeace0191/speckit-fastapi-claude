# Tasks: To-Do List Web App

**Input**: Design documents from `specs/001-todo-list-app/`
**Prerequisites**: [plan.md](plan.md) (required), [spec.md](spec.md) (required), [research.md](research.md), [data-model.md](data-model.md), [contracts/items-api.md](contracts/items-api.md), [quickstart.md](quickstart.md)

**Tests**: Included. The constitution (principle II, test-first, NON-NEGOTIABLE) requires a failing pytest test before each changed endpoint or persistence operation. Client behavior is verified through the manual checks in `quickstart.md`.

**Code location**: Application code is in this repository, at the root (`backend/`, `client/`, `Dockerfile`, `compose.yaml`). Every path below is relative to the repository root.

**Scope note**: Much of the base behavior already exists in the copied code. Each task changes existing code, or adds a test that proves a clarified rule.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story the task belongs to (US1 to US7)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependency declaration and a baseline before changes

- [X] T001 [P] Add `prop-types` to the `dependencies` section of `client/package.json` (constitution I; research R8)
- [X] T002 Record the baseline by running `pytest` in `backend/` and `npm run lint` in `client/`, and note any pre-existing failures in the pull request description

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema ordering column, shared name rule, and shared status message. Every story depends on these.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Write a failing migration test in `backend/spec/persistence/test_sqlite_migration.py`: create a table without `created_seq`, insert rows, run `init()`, and assert the rows are kept and `created_seq` is backfilled in `rowid` order
- [X] T004 Implement the SQLite migration in `backend/src/persistence/sqlite.py` `init()`: if `created_seq` is missing, run `ALTER TABLE todo_items ADD COLUMN created_seq INTEGER`, then `UPDATE todo_items SET created_seq = rowid WHERE created_seq IS NULL` (data-model: `created_seq INTEGER`)
- [X] T005 [P] Implement the MySQL migration in `backend/src/persistence/mysql.py` `init()`: check `information_schema.COLUMNS`; if `created_seq` is absent, run `ALTER TABLE todo_items ADD COLUMN created_seq BIGINT AUTO_INCREMENT UNIQUE` (depends on T043)
- [X] T006 Write a failing ordering test in `backend/spec/persistence/test_sqlite.py`: store three items, complete the first, and assert `get_items()` returns them in insertion order
- [X] T007 Update `backend/src/persistence/sqlite.py`: `store_item` sets `created_seq = COALESCE((SELECT MAX(created_seq) FROM todo_items), 0) + 1`, and `get_items` uses `ORDER BY created_seq` (depends on T004, T006)
- [X] T008 [P] Update `backend/src/persistence/mysql.py`: `get_items` uses `ORDER BY created_seq` (depends on T005, T044)
- [X] T009 Write a failing test in `backend/spec/test_name_rules.py`: `""` is invalid, `"   "` is invalid, `"  Buy milk  "` becomes `"Buy milk"`, 255 characters is valid, and 256 characters is invalid
- [X] T010 Add a reusable `ItemName` type in `backend/src/models.py` that trims whitespace and requires 1 to 255 characters after trimming. Space-only is invalid (data-model validation rules; FR-010, FR-014)
- [X] T011 [P] Create `client/src/components/StatusMessage.jsx`: a `role="status"` / `aria-live="polite"` region that renders a message when one is given and nothing otherwise. All later error messages use it.
- [X] T043 Write a failing test in `backend/spec/persistence/test_mysql_migration.py` (run before T005). Use a fake aiomysql pool, not a live MySQL server (constitution II). Assert that `init()` runs `ALTER TABLE todo_items ADD COLUMN created_seq BIGINT AUTO_INCREMENT UNIQUE` when `information_schema.COLUMNS` has no `created_seq`, and runs no ALTER when the column exists.
- [X] T044 Write a failing test in `backend/spec/persistence/test_mysql_order.py` (run before T008). Use a fake pool. Assert that `get_items()` sends a statement ending in `ORDER BY created_seq`.
- [X] T045 Write a failing test in `backend/spec/persistence/test_mysql_idempotent.py` (run before T022). Use a fake pool. Assert that a second `init()` runs no ALTER when `created_seq` already exists.

**Checkpoint**: Foundation ready. User stories can start.

---

## Phase 3: User Story 1 - Add a to-do item (Priority: P1) 🎯 MVP

**Goal**: A user can add an item with a valid name, and the add control rejects empty or space-only names.

**Independent Test**: Add "Buy milk". It appears last, not completed. An empty or space-only name cannot be submitted (quickstart items 3, 4, 5).

### Tests for User Story 1

- [X] T012 [US1] Write failing tests in `backend/spec/routes/test_addItem.py`: a whitespace-only name returns 422; a 256-character name returns 422; `"  Buy milk "` is stored and returned as `"Buy milk"`; a new item has `completed: false`

### Implementation for User Story 1

- [X] T013 [US1] Apply `ItemName` to `ItemCreate.name` in `backend/src/models.py` (depends on T010, T012)
- [X] T014 [US1] In `client/src/components/AddNewItemForm.jsx`, disable the submit button when `newItem.trim()` is empty. Do not set a `maxLength`, so a name over 255 characters can be submitted and the server's FR-010 message shows (T015)
- [X] T015 [US1] In `client/src/components/AddNewItemForm.jsx`, clear the input after a successful add. After a failed add, keep the typed name in the form and show the message through `StatusMessage` (T011). For a name over 255 characters, the message is "Names must be 255 characters or fewer." (spec FR-010, FR-004; spec Story 1, scenario 4)

**Checkpoint**: User Story 1 is independently testable.

---

## Phase 4: User Story 2 - See all saved items (Priority: P1)

**Goal**: The list shows all items oldest first. Load failures show an error, never the empty message.

**Independent Test**: Save several items, reload, and confirm the order. Stop the backend and reload: the page shows the error with "Try again" (quickstart items 2, 6, 17).

### Tests for User Story 2

- [X] T016 [US2] Write failing tests in `backend/spec/routes/test_getItems.py`: items are returned oldest first, and an empty store returns `[]`

### Implementation for User Story 2

- [X] T017 [US2] In `client/src/components/TodoListCard.jsx`, add a `loadError` state. On a failed load, show `StatusMessage` with a "Try again" button that repeats the load. Never show the empty message on failure (FR-012)
- [X] T018 [US2] In `client/src/components/TodoListCard.jsx`, show "No items yet! Add one above!" only when the load succeeded and `items.length === 0` (FR-003)
- [X] T019 [US2] In `client/src/components/TodoListCard.jsx`, replace closure-based `setItems` updates with functional updates (research R5). Depends on T017, T018 (same file)

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Keep items after a restart (Priority: P1)

**Goal**: Items, their order, and their completion state survive a restart. Running the migration again changes nothing.

**Independent Test**: Add two items, complete one, restart, and confirm all are unchanged (quickstart items 14, 15).

### Tests for User Story 3

- [X] T020 [US3] Write a failing test in `backend/spec/persistence/test_sqlite.py`: items and completion state survive closing and reopening the database file

### Implementation for User Story 3

- [X] T021 [US3] In `backend/src/persistence/sqlite.py` `init()`, make the migration idempotent: a second run does not fail and does not change `created_seq` values (depends on T004, T020)
- [X] T022 [US3] [P] In `backend/src/persistence/mysql.py` `init()`, make the migration idempotent in the same way (depends on T005, T045)

**Checkpoint**: All P1 stories are complete. This is the MVP.

---

## Phase 6: User Story 4 - Mark an item complete or not complete (Priority: P2)

**Goal**: The checkbox toggles completion, sends only `completed`, and reports failures.

**Independent Test**: Toggle one item twice. Each toggle changes state and keeps position (quickstart items 7, 8).

### Tests for User Story 4

- [X] T023 [US4] Write failing tests in `backend/spec/routes/test_updateItem.py`: toggling `completed` true then false returns the original state; a `completed`-only PUT leaves `name` unchanged; an unknown id returns 404 with detail `"Item not found"`

### Implementation for User Story 4

- [X] T024 [US4] In `client/src/components/ItemDisplay.jsx`, make the toggle send only `{ completed }`, not `name`, so a stale name cannot overwrite a later rename
- [X] T025 [US4] In `client/src/components/ItemDisplay.jsx`, show a failure through `StatusMessage`. On 404, show "This item no longer exists" and call a new `onReload` prop passed from `client/src/components/TodoListCard.jsx` (FR-011)
- [X] T026 [US4] In `client/src/components/ItemDisplay.jsx`, fix the class name so only completed items get `completed` (requirement-KR §10 note). Also set the toggle's `aria-label` to `Mark {item.name} as complete` when incomplete and `Mark {item.name} as incomplete` when complete (constitution III)

**Checkpoint**: User Story 4 works independently.

---

## Phase 7: User Story 5 - Delete an item (Priority: P2)

**Goal**: Delete removes an existing item and reports a missing one with 404.

**Independent Test**: Delete an item, reload, and confirm it stays deleted. Delete the same item in a second tab and confirm the message (quickstart items 13, 16).

### Tests for User Story 5

- [X] T027 [US5] Write failing tests in `backend/spec/routes/test_deleteItem.py`: deleting an unknown id returns 404 with detail `"Item not found"`; deleting an existing id returns 200 and the item is absent from `GET /api/items`

### Implementation for User Story 5

- [X] T028 [US5] In `backend/src/routes/items.py` `delete_item`, look the item up with `db.get_item` first and raise `HTTPException(404, "Item not found")` if it is missing (FR-011; research R4)
- [X] T029 [US5] In `client/src/components/ItemDisplay.jsx`, handle delete failures through `StatusMessage` and the same 404 path as T025. Set the remove button's `aria-label` to `Remove {item.name}` (constitution III)

**Checkpoint**: User Story 5 works independently.

---

## Phase 8: User Story 6 - Rename an item (Priority: P2)

**Goal**: A user renames an item through an edit dialog. Cancel changes nothing.

**Independent Test**: Open the rename dialog, change the name, save, and confirm the new name and position. Then rename to blank and confirm Save is disabled (quickstart items 9 to 12).

### Tests for User Story 6

- [X] T030 [US6] Write failing tests in `backend/spec/routes/test_updateItem.py`: a rename is trimmed; a space-only rename returns 422; a 256-character rename returns 422; a rename keeps `completed` and the item's position in `GET /api/items`

### Implementation for User Story 6

- [X] T031 [US6] Apply `ItemName` to `ItemUpdate.name` in `backend/src/models.py`, validated only when `name` is provided (depends on T010, T030)
- [X] T032 [US6] Create `client/src/components/RenameItemDialog.jsx` using a react-bootstrap `Modal`. It has a labelled input prefilled with the current name and no `maxLength`, so an over-length name can be entered. Save is disabled when the trimmed value is empty or longer than 255 characters, and the FR-010 message "Names must be 255 characters or fewer." shows in that case (FR-014). It also has a Cancel button. Focus returns to the trigger on close (research R1, R7)
- [X] T033 [US6] In `client/src/components/ItemDisplay.jsx`, add an edit button with `aria-label="Rename {item.name}"` that opens `RenameItemDialog`. On save, send `PUT` with `{ name }` only, update the item from the response, and show errors through `StatusMessage`. On 404, show "This item no longer exists" and call `onReload`, as in T025 (FR-011) (depends on T032, T029)

**Checkpoint**: User Story 6 works independently.

---

## Phase 9: User Story 7 - See the welcome message (Priority: P3)

**Goal**: The welcome message appears at the top of the page.

**Independent Test**: Open the app and confirm "Hello world!" is above the list (quickstart item 1).

### Tests for User Story 7

- [X] T034 [US7] In `backend/spec/routes/test_getGreeting.py`, confirm the existing tests check the `{"greeting": "Hello world!"}` payload, and add a test if the response shape is not checked

### Implementation for User Story 7

- [X] T035 [US7] Confirm in `client/src/App.jsx` that `Greeting` renders above `TodoListCard` (FR-001). Make changes only if it does not

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Merge gates and validation across all stories

- [X] T036 Run `pytest` in `backend/` and confirm all tests pass (constitution II)
- [X] T037 [P] Run `npm run lint` in `client/` and fix findings in `client/src/` (constitution I)
- [X] T038 [P] Run `npm run build` in `client/` and confirm the output is copied to `backend/src/static`
- [X] T039 Run `docker build --target test .` from the repository root; the `test` stage must pass before the `final` image is built (constitution II; NFR-04)
- [ ] T040 [P] Run the keyboard and screen-reader pass in `quickstart.md` item 18 across all controls in `client/src/components/`. Confirm each toggle, rename, and remove control announces its action and item name. Confirm every interactive control shows a visible focus indicator, and that text and controls meet WCAG 2.1 AA contrast (4.5:1 for normal text), using a browser contrast checker (constitution III)
- [ ] T041 Measure the load time for a 100-item list on the SQLite backend, and record the result to set `TODO(PERF_BUDGET)` in the constitution (constitution IV)
- [ ] T042 Run `quickstart.md` items 1 to 17 and 19 to 24 against the built app, and record the outcomes in the pull request description. Items 20 to 23 cover the client bug fixes in T024, T026, T033, and T015 (constitution II, amended). Item 24 covers MySQL persistence. Item 18 is covered by T040

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user stories.
- **User Stories (Phase 3 to 9)**: Depend on Foundational. P1 stories (US1, US2, US3) come first. US4 to US6 are P2. US7 is P3.
- **Polish (Final)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Add)**: After Foundational. Independent.
- **US2 (View)**: After Foundational. Independent of US1 in code, but the list view is easier to test with items from US1.
- **US3 (Persistence)**: After Foundational migration (T004, T005). Independent of US1 and US2.
- **US4 (Toggle)**: After Foundational. Independent.
- **US5 (Delete)**: After Foundational. Shares `ItemDisplay.jsx` with US4, so run T029 after T025 and T026.
- **US6 (Rename)**: After Foundational. Depends on US4 (T024) so a toggle cannot overwrite a rename, and on US5 (T029) for shared error handling.
- **US7 (Welcome)**: After Foundational. Independent.

### Within Each User Story

- Tests come first and must fail before the implementation task (constitution II)
- Model and persistence changes come before the client changes that call them
- Tasks that edit the same file run in order, never in parallel

### Parallel Opportunities

- Setup: T001 alone (T002 follows it)
- Foundational: T005 with T004 (different files); T008 after T005; T011 alongside T009 and T010
- Stories: US1, US2, US3, US4, US7 can be split across people after Foundational, as long as tasks sharing `ItemDisplay.jsx` or `TodoListCard.jsx` are sequenced
- Polish: T037, T038, and T040 can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1 to 3)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (US1), Phase 4 (US2), Phase 5 (US3)
3. Stop and validate with `quickstart.md` items 1 to 8 and 14 to 17
4. The P1 set is a usable, persistent, ordered to-do list

### Incremental Delivery

1. P1 set (above) is the MVP
2. Add US4 (toggle) and US5 (delete), each validated on its own
3. Add US6 (rename), which depends on US4 and US5
4. Add US7 (welcome message) and run Polish

### Parallel Team Strategy

After Foundational: one person takes the backend tasks (`backend/`), another takes the client tasks (`client/`). The two sides meet at the API contract in `contracts/items-api.md`.

---

## Notes

- Each task names an exact file, so it can be run without extra context
- Each [P] task touches a different file from the other [P] tasks in its group
- The spec quality checklist (`checklists/requirements.md`) and the review checklist (`checklists/feature-review.md`) remain unchanged by this file

## Phase 10: Convergence

**Purpose**: Remaining gaps between the spec, plan, tasks, and constitution, found by `/speckit-converge` after `/speckit-implement`. Paths are relative to the repository root.

- [ ] T046 CRITICAL: Run Prettier on `client/src/App.jsx`, `client/src/main.jsx`, and `client/src/components/Greeting.jsx`, then confirm `npx prettier --check "src/**/*.{js,jsx}"` and `npm run lint` both pass, per Constitution I (contradicts: client code MUST be formatted with Prettier before merge)
- [ ] T047 CRITICAL: Add return annotations to every public function: `get_items` -> `List[Item]`, `add_item` -> `Item`, `update_item` -> `Item`, `delete_item` -> `Response` in `backend/src/routes/items.py`; `get_greeting` -> `dict[str, str]` in `backend/src/routes/greeting.py`; `lifespan` -> `AsyncIterator[None]` in `backend/src/main.py`, per Constitution I (partial: annotate all public functions)
- [ ] T048 CRITICAL: Replace the shared SQLite path in `backend/spec/persistence/test_sqlite.py` with a per-test temporary database, using `tmp_path` and `monkeypatch.setattr(db, "LOCATION", ...)` as `test_sqlite_migration.py` does, so no test depends on `SQLITE_DB_LOCATION` or shares a file, per Constitution II (contradicts: SQLite tests MUST use a temporary database path per test)
- [ ] T049 MEDIUM: Add a test to `backend/spec/persistence/test_sqlite.py` (after T048) that renames an item, closes and reopens the database, and asserts the new name is present, per SC-007 (partial: restart of a renamed item is not tested)
- [ ] T050 MEDIUM: Add a test to `backend/spec/routes/test_getItems.py` that lists 100 items through the app and asserts the response arrives in under 2 seconds on the server side, per SC-006 (partial: no automated check; browser render stays with T041)
- [ ] T051 MEDIUM: In `client/src/components/ItemDisplay.jsx`, show a toggle in the list immediately, then revert it through `onItemUpdate` and report the failure through `onActionError` if the request fails, per SC-004 (partial: the toggle waits for the server response before it changes)
- [ ] T052 LOW: Announce successful add, toggle, rename, and delete through the existing live region (`StatusMessage` with `variant="success"`) in `client/src/components/TodoListCard.jsx` and `client/src/components/ItemDisplay.jsx`, per Constitution III SHOULD (partial: only errors are announced)
