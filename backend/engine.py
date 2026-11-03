"""Bounded, seeded single-agent simulation. No LLM or network calls.

Learning is a contextual multi-armed bandit, not Q-learning. Evaluation is frozen.
Exogenous route noise is generated once per seed before any decisions are made.
"""
from copy import deepcopy
from random import Random
from .catalog import ROUTES, SCENARIOS

def scenario_for(config):
    scenario = deepcopy(next(s for s in SCENARIOS if s['id'] == config.scenario_id))
    if config.deadline is not None:
        scenario['deadline'] = config.deadline
    return scenario

def context_key(config):
    # Include controllable objective/noise settings so one policy doesn't silently mix tasks.
    s = scenario_for(config)
    return f"{s['id']}|deadline={s['deadline']:g}|noise={config.noise:g}|reward=v1"

def select_route(agent, visible, memory, available, scenario, clock, policy, config):
    candidates = [r for r in ROUTES if r['id'] in available]
    if not candidates:
        return None, 'No available route; delivery cannot continue.', {}
    evidence = {}
    if agent in ('simple_reflex', 'model_based'):
        observed = visible if agent == 'simple_reflex' else memory
        first = candidates[0]
        if observed.get(first['id'], 1) >= 2:
            chosen = next((r for r in candidates if observed.get(r['id'], 1) < 2), first)
            reason = f"Heavy traffic on {first['id']}; first non-heavy alternative is {chosen['id']}."
        else:
            chosen = first
            reason = f"Default available route {chosen['id']}; current traffic {'unknown' if chosen['id'] not in observed else 'below heavy threshold'}."
        evidence = {'rule': 'heavy_traffic_alternative' if chosen != first else 'default_route', 'observations_used': observed.copy()}
        if agent == 'model_based':
            evidence['memory'] = memory.copy()
            reason += ' Uses remembered observations.' if not visible else ' Updates route beliefs.'
        return chosen, reason, evidence
    predictions = {}
    for r in candidates:
        eta = clock + r['travel'] * scenario['traffic'][ord(r['id']) - 65] * scenario['weather'] + 2
        late = max(0, eta - scenario['deadline'])
        predictions[r['id']] = {'finish': round(eta, 3), 'cost': r['cost'], 'score': round(eta + r['cost']/20 + 4*late, 3)}
    evidence['predictions'] = predictions
    if agent == 'goal_based':
        feasible = [r for r in candidates if predictions[r['id']]['finish'] <= scenario['deadline']]
        chosen = min(feasible, key=lambda r: (r['cost'], r['id'])) if feasible else min(candidates, key=lambda r: predictions[r['id']]['finish'])
        evidence['goal_feasible'] = bool(feasible)
        reason = f"Cheapest deadline-feasible plan: {chosen['id']}." if feasible else f"Deadline infeasible; fastest available fallback: {chosen['id']}."
    elif agent == 'utility_based':
        chosen = min(candidates, key=lambda r: (predictions[r['id']]['score'], r['id']))
        reason = f"Route {chosen['id']} minimizes time + cost/20 + 4×lateness ({predictions[chosen['id']]['score']:.2f})."
    elif agent == 'hierarchical':
        chosen = min(candidates, key=lambda r: predictions[r['id']]['finish'])
        evidence['task_stack'] = ['deliver_order', 'navigate', 'select_fastest_route']
        reason = f"Navigation subtask chooses fastest route {chosen['id']}; handoff waits for arrival."
    else:
        values = policy.get(context_key(config), {})
        known = [r for r in candidates if values.get(r['id'], {}).get('count', 0)]
        chosen = max(known, key=lambda r: values[r['id']]['mean']) if known else candidates[0]
        evidence.update({'learned_values': deepcopy(values), 'training': False, 'context': context_key(config)})
        reason = f"Frozen learned policy selects {chosen['id']}." if known else 'Untrained context: default route A (or first available); train to learn alternatives.'
    return chosen, reason, evidence

def simulate(config, policy=None, forced_route=None):
    policy = policy or {}
    s = scenario_for(config)
    rng = Random(config.seed)
    realized = {r['id']: r['travel'] * s['traffic'][i] * s['weather'] * rng.uniform(1-config.noise, 1+config.noise) for i, r in enumerate(ROUTES)}
    memory = {r['id']: s['traffic'][i] for i, r in enumerate(ROUTES)}
    clock, distance, cost, progress, reroutes = 0.0, 0.0, 0.0, 0.0, 0
    trace = []
    route = None
    def event(action, reason, state, evidence=None):
        trace.append({'step': len(trace), 'time': round(clock, 3), 'action': action, 'reason': reason, 'state': state, 'route': route['id'] if route else None, 'progress': round(progress, 5), 'evidence': evidence or {}})
    event('ACCEPT_ORDER', 'Order accepted; destination and delivery deadline received.', 'accepted', {'traffic': memory.copy(), 'deadline': s['deadline']})
    while clock < 5:
        clock += 1
        event('WAIT', 'Prepare → wait for restaurant; food is not ready.', 'preparing', {'task_stack': ['deliver_order', 'prepare', 'wait_for_food']} if config.agent_id == 'hierarchical' else {})
    visible = {} if s['partial'] else memory.copy()
    event('PICK_UP', 'Preparation complete. Food collected before departure.', 'picked_up', {'visible_traffic': visible, 'remembered_at': 0})
    available = ['A', 'B', 'C']
    route, reason, evidence = select_route(config.agent_id, visible, memory, available, s, clock, policy, config)
    if forced_route:
        route = next(r for r in ROUTES if r['id'] == forced_route)
        reason, evidence = f'Training episode samples route {forced_route}.', {'training': True}
    event('SELECT_ROUTE', reason, 'route_selected', evidence)
    status = 'delivered'
    chosen_route = route['id']
    while progress < 1 and clock < 180 and len(trace) < 250:
        if s['closure'] and route['id'] == 'A' and clock >= 8:
            event('ROAD_CLOSED', 'Route A closes at the emergency junction.', 'in_transit', {'closure_time': 8})
            if config.agent_id == 'simple_reflex':
                status = 'failed'
                event('REPORT_FAILURE', 'Static reflex policy has no recovery rule for a closure.', 'failed')
                break
            # Fictional connector: preserve already incurred cost/distance and charge full
            # alternate route from this emergency junction; no erased travel or teleporting.
            route, reason, evidence = select_route(config.agent_id, memory, memory, ['B', 'C'], s, clock, policy, config)
            progress = 0
            reroutes += 1
            event('REROUTE', reason + ' Previous travel remains charged; alternate starts at junction.', 'in_transit', evidence)
        duration = min(1.0, (1-progress)*realized[route['id']])
        delta = duration / realized[route['id']]
        progress = min(1.0, progress + delta)
        distance += route['distance'] * delta
        cost += route['cost'] * delta
        clock += duration
        event('MOVE', f"Travel on {route['name']}; {progress*100:.0f}% of current leg complete.", 'arrived' if progress >= 1-1e-9 else 'in_transit')
        if progress >= 1-1e-9:
            progress = 1
            break
    if status != 'failed':
        if progress < 1:
            status = 'timed_out'
            event('REPORT_FAILURE', 'Simulation time or action bound reached.', status)
        else:
            clock += 2
            event('HAND_OFF', 'Arrival verified; two minutes to hand off the order.', 'arrived')
            event('CONFIRM_DELIVERY', 'Food collected, customer reached, and handoff complete.', 'delivered')
    delivered = status == 'delivered'
    lateness = max(0, clock - s['deadline']) if delivered else None
    metrics = {'status': status, 'delivered': delivered, 'duration': round(clock, 3), 'cost': round(cost, 3), 'distance': round(distance, 3), 'deadline': s['deadline'], 'deadline_met': delivered and clock <= s['deadline'] + 1e-9, 'lateness': round(lateness, 3) if lateness is not None else None, 'reroutes': reroutes, 'decisions': len(trace), 'initial_route': chosen_route, 'final_route': route['id'], 'reward': round(-(clock + cost/20 + 4*(lateness or 0) + (0 if delivered else 200)), 5)}
    return {'config': config.model_dump(), 'scenario': s, 'metrics': metrics, 'trace': trace, 'environment': {'realized_route_travel': realized, 'noise': config.noise}, 'policy_context': context_key(config)}
