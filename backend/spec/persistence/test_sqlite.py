import os
import aiosqlite
import pytest
import pytest_asyncio
from src.persistence import sqlite as db

LOCATION = os.getenv("SQLITE_DB_LOCATION", "/etc/todos/todo.db")

ITEM = {
    "id": "7aef3d7c-d301-4846-8358-2a91ec9d6be3",
    "name": "Test",
    "completed": False,
}


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    # Teardown any existing connections first
    await db.teardown()
    if os.path.exists(LOCATION):
        try:
            os.unlink(LOCATION)
        except Exception:
            pass
    yield
    await db.teardown()
    if os.path.exists(LOCATION):
        try:
            os.unlink(LOCATION)
        except Exception:
            pass


@pytest.mark.asyncio
async def test_it_initializes_correctly():
    await db.init()


@pytest.mark.asyncio
async def test_it_can_store_and_retrieve_items():
    await db.init()
    await db.store_item(ITEM)

    items = await db.get_items()
    assert len(items) == 1
    assert items[0] == ITEM


@pytest.mark.asyncio
async def test_it_can_update_an_existing_item():
    await db.init()

    initial_items = await db.get_items()
    assert len(initial_items) == 0

    await db.store_item(ITEM)

    updated = dict(ITEM)
    updated["completed"] = not ITEM["completed"]
    await db.update_item(ITEM["id"], updated)

    items = await db.get_items()
    assert len(items) == 1
    assert items[0]["completed"] == (not ITEM["completed"])


@pytest.mark.asyncio
async def test_it_can_remove_an_existing_item():
    await db.init()
    await db.store_item(ITEM)

    await db.remove_item(ITEM["id"])

    items = await db.get_items()
    assert len(items) == 0


@pytest.mark.asyncio
async def test_it_can_get_a_single_item():
    await db.init()
    await db.store_item(ITEM)

    item = await db.get_item(ITEM["id"])
    assert item == ITEM


@pytest.mark.asyncio
async def test_items_stay_in_insertion_order_after_completing_the_first():
    await db.init()
    first = {"id": "a1", "name": "First", "completed": False}
    second = {"id": "b2", "name": "Second", "completed": False}
    third = {"id": "c3", "name": "Third", "completed": False}
    for item in (first, second, third):
        await db.store_item(item)

    await db.update_item("a1", {"name": "First", "completed": True})

    items = await db.get_items()
    assert [i["id"] for i in items] == ["a1", "b2", "c3"]


@pytest.mark.asyncio
async def test_stored_items_get_increasing_created_seq_values():
    await db.init()
    for item_id in ("a1", "b2", "c3"):
        await db.store_item({"id": item_id, "name": item_id, "completed": False})

    async with aiosqlite.connect(db.LOCATION) as conn:
        async with conn.execute("SELECT created_seq FROM todo_items ORDER BY created_seq") as cursor:
            seqs = [row[0] for row in await cursor.fetchall()]

    assert seqs == [1, 2, 3]


@pytest.mark.asyncio
async def test_items_and_completion_survive_reopening_the_database():
    await db.init()
    await db.store_item({"id": "a1", "name": "Kept", "completed": False})
    await db.update_item("a1", {"name": "Kept", "completed": True})
    await db.teardown()

    await db.init()
    items = await db.get_items()
    assert items == [{"id": "a1", "name": "Kept", "completed": True}]
