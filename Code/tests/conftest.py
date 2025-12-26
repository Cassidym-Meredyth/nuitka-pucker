import pytest

class FakeCursor:
    def __init__(self, fetchall_data=None, fetchone_data=None):
        self._fetchall_data = fetchall_data if fetchall_data is not None else []
        self._fetchone_data = fetchone_data
        self.executed = []

    def execute(self, query):
        self.executed.append(query)
        return self

    def fetchall(self):
        return self._fetchall_data

    def fetchone(self):
        return self._fetchone_data

class FakeDB:
    def __init__(self):
        self.queries = []
        self.cursor = FakeCursor()

    def execute(self, statement):
        if isinstance(statement, str):
            self.queries.append(statement)
            return self.cursor.execute(statement)
        if isinstance(statement, list):
            for st in statement:
                self.queries.append(st)
                self.cursor.execute(st)
            return self.cursor
        raise TypeError

    def commit(self):
        self.queries.append("COMMIT")

@pytest.fixture
def fake_db():
    return FakeDB()
