# Data Model: To-Do List Web App

**Date**: 2026-11-14 | **Plan**: [plan.md](plan.md) | **Research**: [research.md](research.md)

## Entity: To-Do Item

Source: spec Key Entities. One shared list (Clarification Q2); items have no relationship to each
other.

| Field | Type (logical) | Rules | Source |
|-------|----------------|-------|--------|
| `id` | identifier text, 36 characters | Unique, assigned by the server at creation, never changed | FR-006 |
| `name` | text | Stored trimmed. 1 to 255 characters after trimming. Space-only is invalid. | FR-003, FR-010, FR-014 |
| `completed` | boolean | Defaults to `false` on creation. Toggled by users. | FR-004, FR-006 |
| `created_seq` | integer, server-assigned | Strictly increasing per insert. Defines list order (oldest first). Never changed by edits. | FR-002 (Q3) |

`created_seq` is internal. It is not returned in the API response, which keeps the public `Item`
shape unchanged.

## Storage table: `todo_items`

### Before (existing)

```text
todo_items (id VARCHAR(36), name VARCHAR(255), completed BOOLEAN)
```

### After (migration adds one column)

**SQLite**

```text
todo_items (id VARCHAR(36), name VARCHAR(255), completed BOOLEAN, created_seq INTEGER)
```

- Insert: `created_seq = COALESCE((SELECT MAX(created_seq) FROM todo_items), 0) + 1`
- Migration: `ALTER TABLE todo_items ADD COLUMN created_seq INTEGER`, then
  `UPDATE todo_items SET created_seq = rowid WHERE created_seq IS NULL`
- List: `SELECT id, name, completed FROM todo_items ORDER BY created_seq`

**MySQL**

```text
todo_items (id VARCHAR(36), name VARCHAR(255), completed BOOLEAN,
            created_seq BIGINT AUTO_INCREMENT UNIQUE)
```

- Insert: database assigns `created_seq` (no change to the insert column list beyond `id, name,
  completed`)
- Migration: `ALTER TABLE todo_items ADD COLUMN created_seq BIGINT AUTO_INCREMENT UNIQUE`, run only
  when the column is absent (check `information_schema.COLUMNS`)
- List: `SELECT id, name, completed FROM todo_items ORDER BY created_seq`

## Validation rules (model layer)

| Operation | Field | Rule | Failure |
|-----------|-------|------|---------|
| Add (`ItemCreate`) | `name` | Trim; length 1 to 255 | 422 |
| Rename (`ItemUpdate.name`) | `name` | If provided: trim; length 1 to 255 | 422 |
| Toggle (`ItemUpdate.completed`) | `completed` | Boolean | 422 (type) |
| Any change to a missing item | `id` | Must exist | 404 `"Item not found"` |

## State transitions

```text
(none) --add--> not completed --toggle--> completed --toggle--> not completed
   any state --rename--> same state (name changes only)
   any state --delete--> (removed; cannot return)
```

Deleting does not reuse the item's `id` or `created_seq`. A new item always receives a higher
`created_seq` than any existing item, so it appears last.

## Ordering guarantee

For any list response, items are sorted by `created_seq` ascending. Completing, uncompleting, or
renaming an item does not change its `created_seq`, so its position is stable (FR-002).
