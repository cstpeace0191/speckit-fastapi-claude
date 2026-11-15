import os
import asyncio
import aiomysql
from typing import List, Optional, Dict, Any

_pool: Optional[aiomysql.Pool] = None


def _read_env_or_file(env_var: str, file_var: str, default: str = "") -> str:
    file_path = os.getenv(file_var)
    if file_path and os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return os.getenv(env_var, default)


async def init() -> None:
    global _pool

    host = _read_env_or_file("MYSQL_HOST", "MYSQL_HOST_FILE", "localhost")
    user = _read_env_or_file("MYSQL_USER", "MYSQL_USER_FILE", "root")
    password = _read_env_or_file("MYSQL_PASSWORD", "MYSQL_PASSWORD_FILE", "")
    database = _read_env_or_file("MYSQL_DB", "MYSQL_DB_FILE", "todos")

    # Retry connection until database is ready (up to 30 seconds)
    max_retries = 30
    retry_interval = 1.0
    for attempt in range(max_retries):
        try:
            _pool = await aiomysql.create_pool(
                host=host,
                port=3306,
                user=user,
                password=password,
                db=database,
                charset="utf8mb4",
                autocommit=True,
                minsize=1,
                maxsize=5,
            )
            break
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Waiting for MySQL at {host}:3306... ({e})")
            await asyncio.sleep(retry_interval)

    assert _pool is not None
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "CREATE TABLE IF NOT EXISTS todo_items ("
                "id VARCHAR(36), "
                "name VARCHAR(255), "
                "completed BOOLEAN"
                ") DEFAULT CHARSET utf8mb4"
            )
            # Add created_seq to tables created before it existed. The database
            # assigns the values, so existing rows get a creation order too.
            await cur.execute(
                "SELECT COUNT(*) FROM information_schema.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'todo_items' "
                "AND COLUMN_NAME = 'created_seq'"
            )
            (column_count,) = await cur.fetchone()
            if column_count == 0:
                await cur.execute(
                    "ALTER TABLE todo_items ADD COLUMN created_seq BIGINT AUTO_INCREMENT UNIQUE"
                )

    print(f"Connected to mysql db at host {host}")


async def teardown() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None


async def get_items() -> List[Dict[str, Any]]:
    global _pool
    if _pool is None:
        await init()
    assert _pool is not None
    async with _pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id, name, completed FROM todo_items ORDER BY created_seq")
            rows = await cur.fetchall()
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "completed": bool(row["completed"]),
                }
                for row in rows
            ]


async def get_item(item_id: str) -> Optional[Dict[str, Any]]:
    global _pool
    if _pool is None:
        await init()
    assert _pool is not None
    async with _pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, name, completed FROM todo_items WHERE id = %s", (item_id,)
            )
            row = await cur.fetchone()
            if not row:
                return None
            return {
                "id": row["id"],
                "name": row["name"],
                "completed": bool(row["completed"]),
            }


async def store_item(item: Dict[str, Any]) -> None:
    global _pool
    if _pool is None:
        await init()
    assert _pool is not None
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO todo_items (id, name, completed) VALUES (%s, %s, %s)",
                (item["id"], item["name"], 1 if item.get("completed") else 0),
            )


async def update_item(item_id: str, item: Dict[str, Any]) -> None:
    global _pool
    if _pool is None:
        await init()
    assert _pool is not None
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE todo_items SET name = %s, completed = %s WHERE id = %s",
                (item["name"], 1 if item.get("completed") else 0, item_id),
            )


async def remove_item(item_id: str) -> None:
    global _pool
    if _pool is None:
        await init()
    assert _pool is not None
    async with _pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM todo_items WHERE id = %s", (item_id,))
