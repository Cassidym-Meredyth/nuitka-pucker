import types
import data


class DummyCursor:
    def __init__(self, fail_selects=False):
        self.fail_selects = fail_selects
        self.executed = []

    def execute(self, q):
        self.executed.append(q)
        if self.fail_selects and q.strip().startswith("SELECT"):
            raise Exception("no tables")
        return self

    def fetchall(self):
        return []


class DummyConn:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = 0

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed += 1


def test_database_init_calls_create_tables(monkeypatch):
    cur = DummyCursor(fail_selects=True)
    conn = DummyConn(cur)

    monkeypatch.setattr(data.sql, "connect", lambda path: conn)

    db = data.Database()

    assert any("PRAGMA key" in q for q in cur.executed)

    assert any("CREATE TABLE" in q for q in cur.executed)
    assert conn.committed >= 1


def test_database_execute_and_commit(monkeypatch):
    cur = DummyCursor(fail_selects=False)
    conn = DummyConn(cur)
    monkeypatch.setattr(data.sql, "connect", lambda path: conn)

    db = data.Database()
    db.execute("SELECT 1")
    db.commit()

    assert "SELECT 1" in cur.executed
    assert conn.committed >= 1
