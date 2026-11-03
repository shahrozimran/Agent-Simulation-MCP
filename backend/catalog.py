"""Documented simulation fixtures; all prices are fictional cost units."""
AGENTS = [
    {"id": "simple_reflex", "name": "Simple Reflex", "short": "Reflex", "color": "#d8b469", "description": "Ordered rules using only the current observation.", "mechanism": "Percept → ordered rule → action"},
    {"id": "model_based", "name": "Model-Based", "short": "Model", "color": "#81b8df", "description": "Retains recent route observations when visibility is lost.", "mechanism": "Percept + memory → belief update → rule → action"},
    {"id": "goal_based", "name": "Goal-Based", "short": "Goal", "color": "#ac9ae7", "description": "Chooses the cheapest predicted plan that meets the deadline; fastest fallback.", "mechanism": "Beliefs + delivery goal → feasible plans → action"},
    {"id": "utility_based", "name": "Utility-Based", "short": "Utility", "color": "#86d5b4", "description": "Minimizes time + cost / 20 + 4 × predicted lateness.", "mechanism": "Route predictions → utility scores → best action"},
    {"id": "learning", "name": "Learning", "short": "Learning", "color": "#eea88b", "description": "Contextual bandit learns mean route reward from completed training deliveries.", "mechanism": "Context → learned route values → action → training feedback"},
    {"id": "hierarchical", "name": "Hierarchical", "short": "Hierarchy", "color": "#d9a6ce", "description": "Decomposes delivery into accept, prepare, navigate, and handoff subtasks.", "mechanism": "Deliver → ordered subtasks → fastest navigation plan"},
]
AGENT_IDS = [a["id"] for a in AGENTS]
SCENARIOS = [
    {"id": "normal", "name": "Clear skies", "subtitle": "Normal traffic · relaxed deadline", "description": "A calm baseline with all three routes available.", "traffic": [1.0, 1.0, 1.0], "weather": 1.0, "deadline": 35.0, "partial": False, "closure": False},
    {"id": "heavy_traffic", "name": "Rush hour", "subtitle": "Heavy traffic · alternate routes", "description": "The direct route is congested. The first clear alternative is not the fastest.", "traffic": [2.2, 1.1, 1.3], "weather": 1.0, "deadline": 35.0, "partial": False, "closure": False},
    {"id": "rain_urgent", "name": "Against the clock", "subtitle": "Rain · heavy traffic · urgent order", "description": "Only the garden route is predicted to meet the default 28-minute deadline.", "traffic": [2.2, 1.1, 1.3], "weather": 1.25, "deadline": 28.0, "partial": False, "closure": False},
    {"id": "partial_visibility", "name": "Signal lost", "subtitle": "Partial observation · memory test", "description": "Traffic is visible at acceptance but missing at pickup. Model-based memory preserves it.", "traffic": [2.2, 1.1, 1.3], "weather": 1.0, "deadline": 30.0, "partial": True, "closure": False},
    {"id": "road_closure", "name": "Unexpected detour", "subtitle": "Road closure · recovery test", "description": "Direct route A closes at minute 8. Adaptive agents can switch at the emergency junction; reflex stops.", "traffic": [1.0, 1.0, 1.0], "weather": 1.0, "deadline": 30.0, "partial": False, "closure": True},
]
ROUTES = [
    {"id": "A", "name": "Market Street", "distance": 5.0, "travel": 10.0, "cost": 100.0},
    {"id": "B", "name": "Riverside Drive", "distance": 8.0, "travel": 16.0, "cost": 150.0},
    {"id": "C", "name": "Garden Avenue", "distance": 6.0, "travel": 12.0, "cost": 120.0},
]
