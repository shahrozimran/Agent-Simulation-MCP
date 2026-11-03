import pytest

@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setenv('SIMULATION_DB', str(tmp_path / 'test.sqlite3'))
