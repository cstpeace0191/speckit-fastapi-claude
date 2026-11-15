import aiosqlite
import pytest
import pytest_asyncio
from src.persistence import sqlite as db

OLD_SCHEMA = "CREATE TABLE todo_items (id VARCHAR(36), name VARCHAR(255), completed BOOLEAN)"


@pytest_asyncio.fixture
async def old_database(tmp_path, monkeypatch):
    # A database created before created_seq existed, with two rows.
    path = str(tmp_path / "todo.db")
    monkeypatch.setattr(db, "LOCATION", path)
    await db.teardown()
    async with aiosqlite.connect(path) as conn:
        await conn.execute(OLD_SCHEMA)
        await conn.execute("INSERT INTO todo_items (id, name, completed) VALUES ('a', 'First', 0)")
        await conn.execute("INSERT INTO todo_items (id, name, completed) VALUES ('b', 'Second', 1)")
        await conn.commit()
    yield path
    await db.teardown()


async def read_rows(path):
    async with aiosqlite.connect(path) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute(
            "SELECT id, name, completed, created_seq FROM todo_items ORDER BY rowid"
        ) as cursor:
            return [dict(row) for row in await cursor.fetchall()]


@pytest.mark.asyncio
async def test_migration_keeps_existing_rows_and_backfills_created_seq(old_database):
    await db.init()
    await db.teardown()

    rows = await read_rows(old_database)
    assert [r["id"] for r in rows] == ["a", "b"]
    assert [r["name"] for r in rows] == ["First", "Second"]
    assert [r["completed"] for r in rows] == [0, 1]
    assert [r["created_seq"] for r in rows] == [1, 2]


@pytest.mark.asyncio
async def test_second_init_leaves_created_seq_unchanged(old_database):
    await db.init()
    await db.teardown()
    await db.init()  # must not fail
    await db.teardown()

    rows = await read_rows(old_database)
    assert [r["created_seq"] for r in rows] == [1, 2]
