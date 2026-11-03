"""Create 18 real baseline runs once; never add fabricated result data."""
from backend import service, storage
from backend.models import ComparisonRequest

if __name__ == '__main__':
    if storage.overview()['total_runs']:
        print('Existing runs found; no demo data added.')
    else:
        for scenario in ['normal', 'heavy_traffic', 'rain_urgent']:
            service.run_comparison(ComparisonRequest(scenario_id=scenario))
        print('Saved 18 measured baseline simulations (six agents × three scenarios).')
