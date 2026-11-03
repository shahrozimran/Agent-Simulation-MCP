import pytest
from backend.catalog import AGENT_IDS
from backend.engine import simulate, select_route
from backend.models import SimulationRequest, ComparisonRequest, TrainingRequest
from backend import service, storage

@pytest.mark.parametrize('agent', AGENT_IDS)
@pytest.mark.parametrize('scenario', ['normal', 'heavy_traffic', 'rain_urgent'])
def test_baseline_lifecycle_and_metrics(agent, scenario):
    result = simulate(SimulationRequest(agent_id=agent, scenario_id=scenario))
    trace, m = result['trace'], result['metrics']
    actions = [t['action'] for t in trace]
    assert m['delivered']
    assert actions.index('PICK_UP') < actions.index('MOVE') < actions.index('CONFIRM_DELIVERY')
    assert [t['time'] for t in trace] == sorted(t['time'] for t in trace)
    assert m['cost'] > 0 and m['distance'] > 0
    assert m['decisions'] < 250
    if scenario == 'normal':
        assert m['duration'] == 17
    if scenario == 'rain_urgent' and agent in ('goal_based', 'utility_based', 'hierarchical'):
        assert m['initial_route'] == 'C'
        assert m['duration'] == 26.5
        assert m['deadline_met']

def test_partial_observation_memory_changes_decision():
    base = SimulationRequest(scenario_id='partial_visibility')
    reflex = simulate(base.model_copy(update={'agent_id':'simple_reflex'}))
    model = simulate(base.model_copy(update={'agent_id':'model_based'}))
    assert reflex['metrics']['initial_route'] == 'A'
    assert model['metrics']['initial_route'] == 'B'
    # Current-only policy must ignore even contradictory historical beliefs.
    scenario = model['scenario']
    args = ('simple_reflex', {}, {}, ['A','B','C'], scenario, 5, {}, base)
    assert select_route(*args)[0] == select_route(*args[:2], {'A':4}, *args[3:])[0]

def test_closure_recovery_preserves_travel_and_static_policy_fails():
    reflex = simulate(SimulationRequest(agent_id='simple_reflex', scenario_id='road_closure'))
    adaptive = simulate(SimulationRequest(agent_id='goal_based', scenario_id='road_closure'))
    assert reflex['metrics']['status'] == 'failed'
    assert not reflex['metrics']['deadline_met']
    assert adaptive['metrics']['delivered']
    assert adaptive['metrics']['reroutes'] == 1
    assert adaptive['metrics']['distance'] > 6  # Previous A travel plus full C leg.
    assert adaptive['metrics']['cost'] > 120
    assert any(t['action'] == 'REROUTE' for t in adaptive['trace'])

def test_impossible_deadline_reports_lateness_truthfully():
    result = simulate(SimulationRequest(agent_id='goal_based', deadline=5))
    assert result['metrics']['delivered'] and not result['metrics']['deadline_met']
    assert result['metrics']['lateness'] > 0
    selection = next(t for t in result['trace'] if t['action']=='SELECT_ROUTE')
    assert selection['evidence']['goal_feasible'] is False

def test_shared_noise_and_repeatability():
    config = ComparisonRequest(scenario_id='heavy_traffic', noise=0.3, seed=99)
    result = service.run_comparison(config)
    draws = [r['environment']['realized_route_travel'] for r in result['runs']]
    assert all(draw == draws[0] for draw in draws)
    again = simulate(SimulationRequest(agent_id='simple_reflex', scenario_id='heavy_traffic', noise=0.3, seed=99))
    assert again['metrics'] == result['runs'][0]['metrics']
    assert result['fair_conditions']

def test_training_persists_and_frozen_evaluation_does_not_change_policy():
    config = SimulationRequest(agent_id='learning', scenario_id='rain_urgent')
    before = service.run_simulation(config)
    result = service.train_learning(TrainingRequest(episodes=100))
    policy = storage.load_policy()
    after = service.run_simulation(config)
    assert sum(v['count'] for v in result['values'].values()) == 100
    assert after['metrics']['initial_route'] == 'C'
    assert after['metrics']['duration'] < before['metrics']['duration']
    assert policy == storage.load_policy()
    assert result['after']['on_time_rate'] == 100
    assert storage.get_run(after['id'])['trace'] == after['trace']

def test_comparison_marks_different_conditions():
    a = service.run_simulation(SimulationRequest(seed=1))
    b = service.run_simulation(SimulationRequest(seed=2))
    assert not service.comparison_summary([a,b])['fair_conditions']
