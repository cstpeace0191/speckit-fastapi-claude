import os
import aiosqlite
from typing import List, Optional, Dict, Any

LOCATION = os.getenv("SQLITE_DB_LOCATION", "/etc/todos/todo.db")
_db: Optional[aiosqlite.Connection] = None


async def init() -> None:
    global _db
    dirname = os.path.dirname(os.path.abspath(LOCATION))
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    if os.getenv("NODE_ENV") != "test" and os.getenv("ENV") != "test":
        print(f"Using sqlite database at {LOCATION}")

    _db = await aiosqlite.connect(LOCATION)
    _db.row_factory = aiosqlite.Row

    await _db.execute(
        "CREATE TABLE IF NOT EXISTS todo_items (id VARCHAR(36), name VARCHAR(255), completed BOOLEAN, created_seq INTEGER)"
    )
    # Migrate databases created before created_seq existed. Existing rows get
    # their rowid as the creation order, so the original order is kept.
    async with _db.execute("PRAGMA table_info(todo_items)") as cursor:
        columns = [row[1] for row in await cursor.fetchall()]
    if "created_seq" not in columns:
        await _db.execute("ALTER TABLE todo_items ADD COLUMN created_seq INTEGER")
    await _db.execute("UPDATE todo_items SET created_seq = rowid WHERE created_seq IS NULL")
    await _db.commit()


async def teardown() -> None:
    global _db
    if _db is not None:
        await _db.close()
        _db = None


async def get_items() -> List[Dict[str, Any]]:
    global _db
    if _db is None:
        await init()
    assert _db is not None
    async with _db.execute("SELECT id, name, completed FROM todo_items ORDER BY created_seq") as cursor:
        rows = await cursor.fetchall()
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "completed": bool(row["completed"]),
            }
            for row in rows
        ]


async def get_item(item_id: str) -> Optional[Dict[str, Any]]:
    global _db
    if _db is None:
        await init()
    assert _db is not None
    async with _db.execute(
        "SELECT id, name, completed FROM todo_items WHERE id = ?", (item_id,)
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "name": row["name"],
            "completed": bool(row["completed"]),
        }


async def store_item(item: Dict[str, Any]) -> None:
    global _db
    if _db is None:
        await init()
    assert _db is not None
    await _db.execute(
        "INSERT INTO todo_items (id, name, completed, created_seq) "
        "VALUES (?, ?, ?, COALESCE((SELECT MAX(created_seq) FROM todo_items), 0) + 1)",
        (item["id"], item["name"], 1 if item.get("completed") else 0),
    )
    await _db.commit()


async def update_item(item_id: str, item: Dict[str, Any]) -> None:
    global _db
    if _db is None:
        await init()
    assert _db is not None
    await _db.execute(
        "UPDATE todo_items SET name = ?, completed = ? WHERE id = ?",
        (item["name"], 1 if item.get("completed") else 0, item_id),
    )
    await _db.commit()


async def remove_item(item_id: str) -> None:
    global _db
    if _db is None:
        await init()
    assert _db is not None
    await _db.execute("DELETE FROM todo_items WHERE id = ?", (item_id,))
    await _db.commit()
