# Feature Specification: To-Do List Web App

**Feature Branch**: `001-todo-list-app` (not a git repository; no branch created)

**Created**: 2026-11-14

**Status**: Draft

**Input**: User description: "requirement-KR.txt: a to-do list web app with a welcome message, item list, add, complete toggle, delete, and data that survives restarts"

## Clarifications

### Session 2026-11-14

- Q: Should users be able to rename an existing to-do item in the app, or should renaming stay out of the interface for now? → A: C (rename through a separate edit control that opens a dialog)
- Q: Should everyone who uses the app share one list, or should each person see only their own items? → A: A (one shared list for everyone; no accounts)
- Q: In what order should the list show items: oldest first, newest first, or incomplete items first? → A: A (oldest first, in the order items were added; completing an item does not move it)
- Q: How fast must a list of 100 items appear after the page opens: within 2 seconds, within 1 second, or no fixed target yet? → A: A (within 2 seconds; confirms SC-006)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a to-do item (Priority: P1)

A user opens the app, types a task name into the form, and submits it. The new task appears in the list as not completed.

**Why this priority**: Adding a task is the core purpose of the app. Without it nothing else is useful.

**Independent Test**: Open the app, add one task with a name, and confirm it appears in the list as not completed.

**Acceptance Scenarios**:

1. **Given** the app is open and the list is empty, **When** the user types "Buy milk" and submits, **Then** "Buy milk" appears in the list as not completed.
2. **Given** the form is empty, **When** the user looks at the submit control, **Then** the control is unavailable and no item can be submitted.
3. **Given** the user submits a name, **When** the item is created, **Then** the form is cleared so the user can add another item.
4. **Given** the user submits a name, **When** the add fails, **Then** the typed name stays in the form and the user sees a message explaining the failure.

---

### User Story 2 - See all saved items (Priority: P1)

A user opens the app and sees every saved to-do item. If there are no items, the app says so and invites the user to add one.

**Why this priority**: Users must see their list to act on it. The empty state also guides first-time users.

**Independent Test**: Save several items, reload the page, and confirm all of them are shown. Then remove them all and confirm the empty message appears.

**Acceptance Scenarios**:

1. **Given** three saved items, **When** the user opens the app, **Then** all three items are shown with their names and completion states.
2. **Given** no saved items, **When** the user opens the app, **Then** the message "No items yet! Add one above!" is shown.

---

### User Story 3 - Keep items after a restart (Priority: P1)

A user adds items, the service is stopped and started again (or the page is reloaded after a restart), and the same items are still there with the same completion states.

**Why this priority**: A to-do list that loses data is not trustworthy. This is required for the app to be used at all.

**Independent Test**: Add two items, mark one complete, restart the service, and confirm both items and the completion state are unchanged.

**Acceptance Scenarios**:

1. **Given** saved items, **When** the service restarts, **Then** every item is still present with its name and completion state.
2. **Given** an item was deleted before a restart, **When** the service restarts, **Then** the item remains deleted.

---

### User Story 4 - Mark an item complete or not complete (Priority: P2)

A user clicks the checkbox icon on an item to mark it complete. Clicking it again marks it not complete.

**Why this priority**: Tracking progress is the second core action after adding.

**Independent Test**: Click the checkbox on one item twice and confirm the state changes each time and is shown clearly.

**Acceptance Scenarios**:

1. **Given** a not-completed item, **When** the user activates its checkbox, **Then** the item shows as completed.
2. **Given** a completed item, **When** the user activates its checkbox, **Then** the item shows as not completed.

---

### User Story 5 - Delete an item (Priority: P2)

A user clicks the trash icon on an item and the item is removed from the list.

**Why this priority**: Users need to remove items they no longer need, but this is less frequent than adding or completing.

**Independent Test**: Delete one item and confirm it no longer appears in the list, including after a reload.

**Acceptance Scenarios**:

1. **Given** an item in the list, **When** the user activates its trash icon, **Then** the item is removed from the list.
2. **Given** an item was just deleted, **When** the user reloads the page, **Then** the item does not come back.

---

### User Story 6 - Rename an item (Priority: P2)

A user clicks a separate edit control on an item. A dialog opens with the current name filled in. The user changes the name and saves, and the list shows the new name. Cancelling leaves the name unchanged.

**Why this priority**: Fixing a typo or updating a task is common, but users can work around it by deleting and re-adding the item.

**Independent Test**: Open the edit dialog for one item, change its name, save, and confirm the new name appears in the list and after a reload. Then repeat with Cancel and confirm the name is unchanged.

**Acceptance Scenarios**:

1. **Given** an item in the list, **When** the user activates its edit control, **Then** a dialog opens with the item's current name filled in.
2. **Given** the edit dialog is open, **When** the user changes the name and saves, **Then** the list shows the new name, and the new name persists after a reload.
3. **Given** the edit dialog is open, **When** the user clears the name or enters only spaces, **Then** saving is unavailable and the item keeps its previous name.
4. **Given** the edit dialog is open, **When** the user cancels, **Then** the dialog closes and the item keeps its previous name.

---

### User Story 7 - See the welcome message (Priority: P3)

A user opens the app and sees a welcome message at the top of the page.

**Why this priority**: It is a small presentational element and does not affect the core task flow.

**Independent Test**: Open the app and confirm the welcome message is visible at the top.

**Acceptance Scenarios**:

1. **Given** the app is running, **When** the user opens it, **Then** the welcome message "Hello world!" is shown at the top of the page.

---

### Edge Cases

- What happens when the user submits a name made only of spaces? It MUST be treated as empty and rejected (see Assumptions).
- What happens when the name is longer than 255 characters? The item MUST NOT be created, and the user MUST be told why.
- What happens when the list cannot be loaded because the service is unavailable? The app MUST show an error message and MUST NOT show the empty-state message, because that would falsely suggest there are no items.
- What happens when a user toggles or deletes an item that another user or tab has already deleted? The app MUST tell the user the item no longer exists and MUST refresh the list.
- What happens when the list has many items (for example, 100)? All items MUST still be shown, and the list MUST remain usable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST display a welcome message at the top of the page, provided by the service.
- **FR-002**: The system MUST display all saved items, each with its name and completion state, in the order they were added (oldest first). Completing or uncompleting an item MUST NOT change its position.
- **FR-003**: When there are no saved items, the system MUST display "No items yet! Add one above!".
- **FR-004**: Users MUST be able to add an item by entering a name. The name MUST contain at least one character.
- **FR-005**: The submit control for adding an item MUST be unavailable while the name is empty.
- **FR-006**: The system MUST assign each new item a unique identifier and mark it as not completed.
- **FR-007**: Users MUST be able to toggle an item's completion state. Each activation reverses the current state.
- **FR-008**: Users MUST be able to delete an item. A deleted item MUST NOT appear again.
- **FR-009**: All items and their completion states MUST persist across service restarts and page reloads.
- **FR-010**: Item names MUST NOT exceed 255 characters. Longer names MUST be rejected with the message "Names must be 255 characters or fewer."
- **FR-011**: When an action targets an item that no longer exists, the system MUST inform the user and refresh the list.
- **FR-012**: When the list cannot be loaded, the system MUST show an error message instead of the empty-state message.
- **FR-013**: Users MUST be able to rename an item through a separate edit control that opens an edit dialog. The dialog MUST NOT open from clicking the item name. Renaming MUST keep the item's position in the list and its completion state.
- **FR-014**: A renamed item MUST follow the same name rules as a new item (at least one non-space character, at most 255 characters). Saving an invalid name MUST be blocked and the previous name kept.
- **FR-015**: Cancelling the edit dialog MUST leave the item unchanged.

### Key Entities

- **To-Do Item**: One task the user wants to track. Attributes: a unique identifier assigned by the system, a name (text, 1 to 255 characters), and a completion state (completed or not completed). Items have no relationship to other items.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time user can add their first item within 30 seconds of opening the app, without instructions.
- **SC-002**: In restart testing, 100% of saved items and their completion states are unchanged after the service is restarted.
- **SC-003**: 100% of attempts to submit an empty name are blocked, and no item is created from them.
- **SC-004**: A user can change an item's completion state with a single action, and the change is visible immediately.
- **SC-005**: Every action in the app (add, toggle, delete) can be completed using only the keyboard.
- **SC-006**: A list of 100 items is fully displayed within 2 seconds of opening the app.
- **SC-007**: A user can rename an item in under 20 seconds, and in restart testing the new name is still present afterward.

## Assumptions

- A name made only of spaces counts as empty and is rejected.
- There are no user accounts. All items form one shared list for everyone who uses the app (confirmed in the 2026-11-14 clarification session).
- Several people may use the shared list at the same time. If two people change the same item, the last save wins, and the app does not lock items. A person who acts on an item another person has deleted sees the "no longer exists" message (FR-011).
- Users cannot choose a sort order. Items always appear oldest first (confirmed in the 2026-11-14 clarification session).
- Technical choices (languages, frameworks, storage, service interfaces, deployment) are not part of this specification. They belong to the planning phase and are described in `requirement-KR.txt`.
- Accessibility and performance expectations come from the project constitution (`.specify/memory/constitution.md`).
