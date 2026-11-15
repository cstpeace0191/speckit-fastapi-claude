import pytest
from src.persistence import mysql
from spec.persistence.fake_mysql import FakePool, FakeServer


@pytest.fixture(autouse=True)
def reset_pool():
    mysql._pool = None
    yield
    mysql._pool = None


@pytest.mark.asyncio
async def test_get_items_orders_by_created_seq():
    server = FakeServer(columns=("created_seq",))
    mysql._pool = FakePool(server)

    await mysql.get_items()

    select_statements = [" ".join(s.split()) for s in server.statements if "FROM todo_items" in s]
    assert select_statements, "get_items must query todo_items"
    assert select_statements[-1].endswith("ORDER BY created_seq")
