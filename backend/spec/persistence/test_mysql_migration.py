import pytest
from unittest.mock import AsyncMock, patch
from src.persistence import mysql
from spec.persistence.fake_mysql import FakePool, FakeServer

ALTER = "ALTER TABLE todo_items ADD COLUMN created_seq BIGINT AUTO_INCREMENT UNIQUE"


@pytest.fixture(autouse=True)
def reset_pool():
    mysql._pool = None
    yield
    mysql._pool = None


def alter_statements(server):
    return [" ".join(s.split()) for s in server.statements if " ".join(s.split()) == ALTER]


@pytest.mark.asyncio
async def test_init_adds_created_seq_when_column_is_missing():
    server = FakeServer(columns=())
    with patch.object(mysql.aiomysql, "create_pool", AsyncMock(return_value=FakePool(server))):
        await mysql.init()

    assert len(alter_statements(server)) == 1


@pytest.mark.asyncio
async def test_init_does_not_alter_when_created_seq_exists():
    server = FakeServer(columns=("created_seq",))
    with patch.object(mysql.aiomysql, "create_pool", AsyncMock(return_value=FakePool(server))):
        await mysql.init()

    assert alter_statements(server) == []
