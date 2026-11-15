# Quickstart: To-Do List Web App

**Date**: 2026-11-14 | **Plan**: [plan.md](plan.md) | **Contract**: [contracts/items-api.md](contracts/items-api.md)

These steps prove the feature works end to end. They do not include implementation code. The code
lives at the root of this repository (`backend/`, `client/`, `Dockerfile`, `compose.yaml`).

## Prerequisites

- Python 3.12, Node.js 22, and `npm`
- Optional: Docker Desktop with Compose v2 (for the MySQL and `final` image checks)

## 1. Backend tests (must pass before merge)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
```

Expected: all tests pass, including the new ordering, validation, migration, and 404-on-delete
tests added under `backend/spec/`.

## 2. Run the app locally (SQLite)

```bash
set SQLITE_DB_LOCATION=%CD%\data\todo.db
python main.py
```

Open `http://localhost:3000`. For frontend development, run `npm run dev` in `client/`
(port 5173, `/api` proxied to 3000).

## 3. Client checks (must pass before merge)

```bash
cd ../client
npm install
npm run lint
npm run build
```

`npm run build` copies the output to `backend/src/static`.

## 4. Manual acceptance checks

Run the app and check each item. Each line maps to a spec acceptance scenario.

| # | Check | Expected | Spec |
|---|-------|----------|------|
| 1 | Open the app | Welcome text "Hello world!" at top | Story 7, FR-001 |
| 2 | Open the app with no items | "No items yet! Add one above!" | Story 2, FR-003 |
| 3 | Type nothing; look at Add | Add is disabled | Story 1, FR-005 |
| 4 | Type three spaces; look at Add | Add is disabled | FR-004, R3 |
| 5 | Add "Buy milk" | Appears last, not completed; input clears | Story 1 |
| 6 | Add "Call Ann", "Pay rent" | List shows Buy milk, Call Ann, Pay rent in that order | FR-002 |
| 7 | Complete "Buy milk" | Stays in first position; shows completed | Story 4, FR-002 |
| 8 | Uncomplete "Buy milk" | Shows not completed; position unchanged | Story 4 |
| 9 | Open rename for "Call Ann" | Dialog opens with "Call Ann" filled in | Story 6 |
| 10 | Rename to "Call Ann Lee" and save | List shows new name; position unchanged | Story 6, FR-013 |
| 11 | Rename, clear the text; then rename to 256 characters | Save is disabled in both cases. The 256-character case shows "Names must be 255 characters or fewer."; name unchanged | Story 6, FR-014, FR-010 |
| 12 | Rename, then Cancel | Dialog closes; name unchanged | FR-015 |
| 13 | Delete "Pay rent" | Removed from list | Story 5, FR-008 |
| 14 | Reload the page | Deleted item stays deleted; order and completion persist | Story 3, FR-009 |
| 15 | Stop and restart the backend; reload | All items, order, and completion unchanged | Story 3, SC-002 |
| 16 | In a second tab, delete an item; then toggle it in the first tab | First tab shows "This item no longer exists" and refreshes | FR-011 |
| 17 | Stop the backend; reload the page | Error message with "Try again"; no "No items yet!" text | FR-012 |
| 18 | Tab through the page with the keyboard only | Every control reachable; focus visible; Remove button announces "Remove {name}" | SC-005, constitution III |
| 19 | Add 100 items (script or repeated adds); reload | All 100 appear within 2 seconds, oldest first | SC-006 |
| 20 | Rename "Call Ann" to "Call Ann Lee" in the open list, then toggle its checkbox without reloading | The name stays "Call Ann Lee" after the toggle (no stale name sent) | Story 6, FR-007, research R5 |
| 21 | Tab A and tab B both show "Call Ann". In tab B, delete it. In tab A, rename it to "Call Ann Lee" and save | Tab A shows "This item no longer exists", and the list refreshes without "Call Ann" | FR-011 |
| 22 | (a) Stop the backend after the page loads. Type "Buy milk" and click Add. (b) Restart the backend. Type a 256-character name and click Add | (a) The typed name stays in the form, and a message explains the add failed. (b) The message "Names must be 255 characters or fewer." shows, and the typed name stays in the form | Story 1, scenario 4; FR-010 |
| 23 | Inspect a completed item and an incomplete item | Completed item has class `completed`; incomplete item does not. The toggle's accessible name is "Mark Buy milk as complete" or "Mark Buy milk as incomplete" | constitution III |
| 24 | With MySQL in Compose: add items, complete one, run `docker compose restart backend`, reload | All items, their order, and completion state are unchanged | FR-009, constitution (Additional Constraints) |

## 5. Docker checks (for the `final` image)

```bash
docker build --target test -t todo-test .
docker build -t todo-app .
docker run -p 3000:3000 todo-app
```

Expected: the `test` stage passes and the build continues to `final`. Then check items 1 to 15
against `http://localhost:3000`.

## 6. Migration check (existing data)

1. Using the pre-change code, create a SQLite database with several items.
2. Start the new code against that same file.
3. Expected: the app starts, no data is lost, and the existing items appear in their previous
   order (backfilled from `rowid`, see R2).
