"""In-memory stand-in for an aiomysql pool.

The constitution forbids tests that need a running MySQL server, so the MySQL
persistence tests use this fake. It records every SQL statement and tracks the
columns of todo_items, which is enough to check migration behavior.
"""


class FakeServer:
    def __init__(self, columns=()):
        self.columns = set(columns)
        self.statements = []


class FakeCursor:
    def __init__(self, server):
        self.server = server
        self._result = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, sql, params=None):
        self.server.statements.append(sql)
        normalized = " ".join(sql.split())
        self._result = None
        if normalized.startswith("SELECT COUNT(*) FROM information_schema.COLUMNS"):
            self._result = (1 if "created_seq" in self.server.columns else 0,)
        elif normalized.startswith("ALTER TABLE todo_items ADD COLUMN created_seq"):
            self.server.columns.add("created_seq")
        elif normalized.startswith("SELECT"):
            self._result = []

    async def fetchone(self):
        return self._result

    async def fetchall(self):
        return self._result if isinstance(self._result, list) else []


class FakeConnection:
    def __init__(self, server):
        self.server = server

    def cursor(self, *args, **kwargs):
        return FakeCursor(self.server)


class _Acquire:
    def __init__(self, server):
        self.conn = FakeConnection(server)

    async def __aenter__(self):
        return self.conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakePool:
    def __init__(self, server):
        self.server = server

    def acquire(self):
        return _Acquire(self.server)

    def close(self):
        pass

    async def wait_closed(self):
        pass
