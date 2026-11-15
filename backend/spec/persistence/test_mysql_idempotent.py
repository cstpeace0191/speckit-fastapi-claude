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


@pytest.mark.asyncio
async def test_second_init_does_not_run_the_migration_again():
    server = FakeServer(columns=())
    with patch.object(mysql.aiomysql, "create_pool", AsyncMock(return_value=FakePool(server))):
        await mysql.init()
        mysql._pool = None
        await mysql.init()

    alters = [" ".join(s.split()) for s in server.statements if " ".join(s.split()) == ALTER]
    assert len(alters) == 1
