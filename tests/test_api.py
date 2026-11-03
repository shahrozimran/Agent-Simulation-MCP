import csv
import io
from fastapi.testclient import TestClient
from backend.api import app

def test_api_run_retrieve_export_and_stats():
    with TestClient(app) as client:
        assert client.get('/api/health').json()['database'] == 'connected'
        assert len(client.get('/api/catalog').json()['agents']) == 6
        created = client.post('/api/runs', json={'agent_id':'goal_based'}).json()
        saved = client.get('/api/runs/'+created['id']).json()
        assert saved == created
        export = client.get('/api/runs/'+created['id']+'/export?format=csv')
        assert 'attachment' in export.headers['content-disposition']
        row = next(csv.DictReader(io.StringIO(export.text)))
        assert float(row['duration']) == 26.5
        assert client.get('/api/overview').json()['total_runs'] == 1
        assert client.get('/api/runs/'+created['id']+'/export').json() == created

def test_validation_and_missing_results():
    with TestClient(app) as client:
        for body in [{'agent_id':'invented'}, {'noise':-1}, {'deadline':0}, {'seed':-1}, {'secret':'x'}]:
            assert client.post('/api/runs', json=body).status_code == 422
        assert client.get('/api/runs/missing').status_code == 404
        assert client.get('/api/runs?limit=999999').status_code == 422
        assert client.post('/api/training', json={'episodes':1001}).status_code == 422
        assert client.post('/api/comparisons', json={'agent_ids':[]}).status_code == 422

def test_comparison_learning_and_mcp_configuration():
    with TestClient(app) as client:
        result = client.post('/api/comparisons', json={}).json()
        assert len(result['runs']) == 6
        assert len(set(r['id'] for r in result['runs'])) == 6
        assert client.get('/api/overview').json()['total_runs'] == 6
        compared = client.post('/api/compare', json={'run_ids':[r['id'] for r in result['runs']]}).json()
        assert compared['fair_conditions']
        assert client.post('/api/training', json={'episodes':50}).status_code == 200
        assert client.get('/api/policy').json()
        assert client.get('/api/overview').json()['training_episodes'] == 50
        config = client.get('/api/mcp').json()
        assert len(config['tools']) == 8 and config['llm_required'] is False
