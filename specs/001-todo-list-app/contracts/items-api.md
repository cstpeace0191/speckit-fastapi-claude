# Contract: Item HTTP API

**Date**: 2026-11-14 | **Plan**: [../plan.md](../plan.md) | **Data model**: [../data-model.md](../data-model.md)

This is the public HTTP interface the React client uses. Each endpoint is also served without the
`/api` prefix (hidden from the OpenAPI schema), which stays unchanged.

Changes from the current code are marked **[changed]**. Everything else is existing behavior.

## Item object

```json
{ "id": "3f2c9a1e-…", "name": "Buy milk", "completed": false }
```

`created_seq` is not exposed. Order is defined by the list endpoint.

## GET /api/greeting

- **200**: `{ "greeting": "Hello world!" }` (unchanged; FR-001)

## GET /api/items

- **200**: array of Item objects, **oldest first** (**[changed]**, FR-002). An empty list when there
  are no items.
- **500 / network failure**: the client shows a load error, not an empty list (FR-012).

## POST /api/items

Request:

```json
{ "name": "Buy milk" }
```

- **200**: the created Item, `completed: false`, name trimmed (**[changed]** trimming, FR-003,
  FR-004)
- **422**: name is missing, empty, only spaces, or longer than 255 characters (**[changed]**
  validation, FR-010)

## PUT /api/items/{item_id}

Partial update. Fields not sent keep their current value (FR-005).

Request (any subset):

```json
{ "name": "Buy oat milk", "completed": true }
```

- **200**: the updated Item (**[changed]** name trimmed)
- **404**: `{ "detail": "Item not found" }` if `item_id` does not exist (FR-005, FR-011)
- **422**: `name` is provided but empty, space-only, or longer than 255 characters
  (**[changed]**, FR-014)

Renaming is sent as `PUT` with `name` only, from the rename dialog (Clarification Q1).

## DELETE /api/items/{item_id}

- **200**: empty body when the item was deleted (FR-008)
- **404**: `{ "detail": "Item not found" }` if `item_id` does not exist (**[changed]**, FR-011).
  Currently returns 200 for a missing item.

## Error handling expectations for the client

| Status | Client behavior |
|--------|-----------------|
| 200 | Update local state from the response |
| 404 | Show "This item no longer exists", reload the list (FR-011) |
| 422 | Show the reason near the input (FR-003, FR-014) |
| 5xx or network error | Show a visible error message in the live region; keep the item unchanged |

## Compatibility

- Responses for existing successful calls keep their shape. Only ordering, trimming, and the new
  error statuses change.
- Callers that already send valid names see no difference.
