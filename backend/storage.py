import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def db_path():
    return Path(os.environ.get('SIMULATION_DB', str(ROOT / 'data' / 'simulation.sqlite3')))

@contextmanager
def connection():
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path, timeout=30) as db:
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, batch_id TEXT, agent_id TEXT NOT NULL, scenario_id TEXT NOT NULL, payload TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS policy (context TEXT NOT NULL, route TEXT NOT NULL, samples INTEGER NOT NULL, mean REAL NOT NULL, PRIMARY KEY (context, route))')
        db.execute('CREATE TABLE IF NOT EXISTS training (id TEXT PRIMARY KEY, created_at TEXT NOT NULL, payload TEXT NOT NULL)')
        yield db

def load_policy(db=None):
    if db is None:
        with connection() as db:
            return load_policy(db)
    policy = {}
    for row in db.execute('SELECT * FROM policy'):
        policy.setdefault(row['context'], {})[row['route']] = {'count': row['samples'], 'mean': row['mean']}
    return policy

def insert_run(db, run):
    db.execute('INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?)', (run['id'], run['created_at'], run.get('batch_id'), run['config']['agent_id'], run['config']['scenario_id'], json.dumps(run)))

def list_runs(limit=100, offset=0):
    with connection() as db:
        rows = db.execute('SELECT payload FROM runs ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?', (limit, offset)).fetchall()
    return [{k:v for k,v in json.loads(row['payload']).items() if k not in ('trace', 'environment')} for row in rows]

def get_run(run_id):
    with connection() as db:
        row = db.execute('SELECT payload FROM runs WHERE id=?', (run_id,)).fetchone()
    if not row:
        raise ValueError(f'Run {run_id} was not found.')
    return json.loads(row['payload'])

def overview():
    with connection() as db:
        count = db.execute('SELECT COUNT(*) FROM runs').fetchone()[0]
        # Aggregate all persisted results, not just the first history page.
        success = db.execute("SELECT COUNT(*) FROM runs WHERE json_extract(payload, '$.metrics.deadline_met')=1").fetchone()[0]
        average = db.execute("SELECT AVG(json_extract(payload, '$.metrics.duration')) FROM runs WHERE json_extract(payload, '$.metrics.delivered')=1").fetchone()[0]
        training = db.execute('SELECT payload FROM training ORDER BY created_at DESC LIMIT 1').fetchone()
        samples = db.execute('SELECT COALESCE(SUM(samples),0) FROM policy').fetchone()[0]
    return {'total_runs': count, 'on_time_rate': round(success/count*100, 1) if count else 0, 'average_duration': round(average, 2) if average is not None else None, 'training_episodes': samples, 'last_training': json.loads(training['payload']) if training else None}
