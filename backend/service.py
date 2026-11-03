from copy import deepcopy
from datetime import datetime, timezone
from random import Random
from uuid import uuid4
import json
from . import storage
from .engine import simulate, context_key
from .models import SimulationRequest, ComparisonRequest, TrainingRequest

def stamp():
    return datetime.now(timezone.utc).isoformat()

def run_simulation(config: SimulationRequest):
    policy = storage.load_policy()
    run = simulate(config, policy)
    run.update(id=str(uuid4()), created_at=stamp(), policy_snapshot=policy.get(context_key(config), {}))
    with storage.connection() as db:
        storage.insert_run(db, run)
    return run

def comparison_summary(runs):
    # Rank completed deliveries ahead of failures, then deadline, time, cost.
    ordered = sorted(runs, key=lambda r: (not r['metrics']['delivered'], not r['metrics']['deadline_met'], r['metrics']['duration'], r['metrics']['cost']))
    settings = [tuple(r['config'][k] for k in ('scenario_id', 'seed', 'deadline', 'noise')) for r in runs]
    return {'runs': runs, 'ranking': [r['id'] for r in ordered], 'fair_conditions': len(set(settings)) <= 1, 'ranking_rule': 'Delivered first, then on time, then shortest duration, then lowest cost. This is an external ranking, not agent utility.'}

def run_comparison(config: ComparisonRequest):
    batch = str(uuid4())
    policy = storage.load_policy()
    runs = []
    for agent in dict.fromkeys(config.agent_ids):
        request = SimulationRequest(agent_id=agent, **config.model_dump(exclude={'agent_ids'}))
        run = simulate(request, policy)
        run.update(id=str(uuid4()), batch_id=batch, created_at=stamp(), policy_snapshot=policy.get(context_key(request), {}))
        runs.append(run)
    with storage.connection() as db:
        for run in runs:
            storage.insert_run(db, run)
    return {'batch_id': batch, **comparison_summary(runs)}

def train_learning(request: TrainingRequest):
    rng = Random(request.seed)
    base = SimulationRequest(agent_id='learning', scenario_id=request.scenario_id, seed=request.seed, noise=0)
    context = context_key(base)
    # Hold out seeds from the training stream for before/after evaluation.
    evaluation = [base.model_copy(update={'seed': request.seed + 100000 + i}) for i in range(30)]
    with storage.connection() as db:
        db.execute('BEGIN IMMEDIATE')
        policy = storage.load_policy(db)
        before = [simulate(c, policy)['metrics'] for c in evaluation]
        values = policy.setdefault(context, {})
        history = []
        for episode in range(request.episodes):
            unknown = [r for r in 'ABC' if not values.get(r, {}).get('count')]
            explore = bool(unknown) or rng.random() < request.epsilon
            chosen = unknown[0] if unknown else rng.choice(list('ABC')) if explore else max(values, key=lambda r: values[r]['mean'])
            config = base.model_copy(update={'seed': rng.randrange(2147483647)})
            result = simulate(config, policy, forced_route=chosen)
            reward = result['metrics']['reward']
            v = values.setdefault(chosen, {'count': 0, 'mean': 0.0})
            v['count'] += 1
            v['mean'] += (reward - v['mean']) / v['count']
            history.append({'episode': episode+1, 'route': chosen, 'reward': reward, 'exploration': explore})
        after = [simulate(c, policy)['metrics'] for c in evaluation]
        def summary(metrics):
            return {'mean_duration': round(sum(m['duration'] for m in metrics)/len(metrics), 3), 'mean_reward': round(sum(m['reward'] for m in metrics)/len(metrics), 3), 'on_time_rate': round(sum(m['deadline_met'] for m in metrics)/len(metrics)*100, 1), 'runs': len(metrics)}
        result = {'id': str(uuid4()), 'created_at': stamp(), 'request': request.model_dump(), 'context': context, 'values': deepcopy(values), 'history': history, 'before': summary(before), 'after': summary(after), 'evaluation_note': '30 held-out seeds; noise=0, so this measures the fixed scenario only. Training uses the contextual-bandit reward v1. Evaluation never updates policy.'}
        for route, v in values.items():
            db.execute('INSERT INTO policy VALUES (?, ?, ?, ?) ON CONFLICT(context, route) DO UPDATE SET samples=excluded.samples, mean=excluded.mean', (context, route, v['count'], v['mean']))
        db.execute('INSERT INTO training VALUES (?, ?, ?)', (result['id'], result['created_at'], json.dumps(result)))
    return result
