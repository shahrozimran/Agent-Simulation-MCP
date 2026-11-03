"""Use stdio by default; --http serves a loopback Streamable HTTP endpoint."""
import argparse
from mcp.server.fastmcp import FastMCP
from backend.catalog import AGENTS, SCENARIOS
from backend.models import SimulationRequest, ComparisonRequest, TrainingRequest
from backend import service, storage

mcp = FastMCP('Agent Simulation Lab', host='127.0.0.1', port=8001)

@mcp.tool()
def list_agents() -> list[dict]:
    """List six agent architectures, mechanisms, and supported agent IDs."""
    return AGENTS

@mcp.tool()
def list_scenarios() -> list[dict]:
    """List available fictional delivery scenarios, traffic, and deadlines."""
    return SCENARIOS

@mcp.tool()
def run_simulation(agent_id: str = 'goal_based', scenario_id: str = 'rain_urgent', seed: int = 42, deadline: float | None = None, noise: float = 0) -> dict:
    """Run and save one bounded simulation. Evaluation does not train the learning agent. Returns metrics and run ID; use get_run for the full trace."""
    run = service.run_simulation(SimulationRequest(agent_id=agent_id, scenario_id=scenario_id, seed=seed, deadline=deadline, noise=noise))
    return {k:v for k,v in run.items() if k not in ('trace', 'environment')}

@mcp.tool()
def run_comparison(scenario_id: str = 'rain_urgent', seed: int = 42, deadline: float | None = None, noise: float = 0) -> dict:
    """Run all six independent agents under identical seeded conditions, save results, and rank them."""
    result = service.run_comparison(ComparisonRequest(scenario_id=scenario_id, seed=seed, deadline=deadline, noise=noise))
    result['runs'] = [{k:v for k,v in r.items() if k not in ('trace', 'environment')} for r in result['runs']]
    return result

@mcp.tool()
def get_run(run_id: str) -> dict:
    """Retrieve a persisted simulation, including complete decision trace and reasoning."""
    return storage.get_run(run_id)

@mcp.tool()
def list_runs(limit: int = 20, offset: int = 0) -> list[dict]:
    """List saved run summaries, newest first; limit must be 1–100, offset nonnegative."""
    if not 1 <= limit <= 100 or offset < 0:
        raise ValueError('limit must be 1–100 and offset must be nonnegative')
    return storage.list_runs(limit, offset)

@mcp.tool()
def compare_runs(run_ids: list[str]) -> dict:
    """Compare 2–100 saved runs. fair_conditions flags mismatched scenarios or seeds."""
    if not 2 <= len(run_ids) <= 100:
        raise ValueError('Provide 2–100 run IDs.')
    result = service.comparison_summary([storage.get_run(i) for i in run_ids])
    result['runs'] = [{k:v for k,v in r.items() if k not in ('trace', 'environment')} for r in result['runs']]
    return result

@mcp.tool()
def train_learning(scenario_id: str = 'rain_urgent', episodes: int = 150, seed: int = 42, epsilon: float = 0.2) -> dict:
    """Explicitly train and persist contextual-bandit route values. Changes future learning-agent evaluations. 10–1000 episodes."""
    result = service.train_learning(TrainingRequest(scenario_id=scenario_id, episodes=episodes, seed=seed, epsilon=epsilon))
    return {k:v for k,v in result.items() if k != 'history'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--http', action='store_true', help='Serve Streamable HTTP instead of stdio')
    parser.add_argument('--port', type=int, default=8001, help='HTTP port (default: 8001)')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    mcp.settings.port = args.port
    mcp.run(transport='streamable-http' if args.http else 'stdio')
