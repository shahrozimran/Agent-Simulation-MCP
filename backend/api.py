import csv
import io
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from .catalog import AGENTS, SCENARIOS, ROUTES
from .models import SimulationRequest, ComparisonRequest, TrainingRequest, CompareSavedRequest
from . import service, storage

app = FastAPI(title='Agent Simulation Lab', version='1.0.0', description='Local simulation API. Six independent agent architectures, persisted traces, and MCP tools.')
app.add_middleware(CORSMiddleware, allow_origins=['http://127.0.0.1:5173', 'http://localhost:5173'], allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

@app.get('/api/health')
def health():
    with storage.connection() as db:
        db.execute('SELECT 1')
    return {'status': 'ok', 'database': 'connected', 'llm_required': False}

@app.get('/api/catalog')
def catalog():
    return {'agents': AGENTS, 'scenarios': SCENARIOS, 'routes': ROUTES}

@app.get('/api/overview')
def overview():
    return storage.overview()

@app.get('/api/runs')
def list_runs(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    return storage.list_runs(limit, offset)

@app.post('/api/runs')
def create_run(request: SimulationRequest):
    return service.run_simulation(request)

def required_run(run_id):
    try:
        return storage.get_run(run_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc)) from exc

@app.get('/api/runs/{run_id}')
def get_run(run_id: str):
    return required_run(run_id)

@app.get('/api/runs/{run_id}/export')
def export_run(run_id: str, format: str = Query('json', pattern='^(json|csv)$')):
    run = required_run(run_id)
    if format == 'json':
        data, mime = json.dumps(run, indent=2), 'application/json'
    else:
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=['run_id', 'agent', 'scenario', *run['metrics'].keys()])
        writer.writeheader()
        writer.writerow({'run_id': run_id, 'agent': run['config']['agent_id'], 'scenario': run['config']['scenario_id'], **run['metrics']})
        data, mime = stream.getvalue(), 'text/csv'
    return Response(data, media_type=mime, headers={'Content-Disposition': f'attachment; filename="run-{run_id}.{format}"'})

@app.post('/api/comparisons')
def create_comparison(request: ComparisonRequest):
    return service.run_comparison(request)

@app.post('/api/compare')
def compare_saved(request: CompareSavedRequest):
    return service.comparison_summary([required_run(run_id) for run_id in request.run_ids])

@app.get('/api/policy')
def policy():
    return storage.load_policy()

@app.post('/api/training')
def train(request: TrainingRequest):
    return service.train_learning(request)

@app.get('/api/mcp')
def mcp_info():
    root = storage.ROOT
    return {'name': 'agent-simulation', 'transport': 'stdio', 'tools': ['list_agents', 'list_scenarios', 'run_simulation', 'run_comparison', 'get_run', 'list_runs', 'compare_runs', 'train_learning'], 'config': {'mcpServers': {'agent-simulation': {'command': str(root / '.venv' / 'Scripts' / 'python.exe'), 'args': [str(root / 'mcp_server.py')]}}}, 'llm_required': False}

dist = storage.ROOT / 'frontend' / 'dist'
if dist.exists():
    app.mount('/', StaticFiles(directory=dist, html=True), name='frontend')
