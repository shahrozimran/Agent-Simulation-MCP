# Local API

Open `/docs` on the running backend for the interactive OpenAPI reference.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Verify API and database |
| GET | `/api/catalog` | Agents, scenarios, routes |
| GET | `/api/overview` | Statistics across all saved runs |
| GET | `/api/runs?limit=100&offset=0` | Paginated summaries (limit 1–500) |
| POST | `/api/runs` | Run one simulation |
| GET | `/api/runs/{id}` | Complete result and trace |
| GET | `/api/runs/{id}/export?format=json` | Download JSON; CSV also supported |
| POST | `/api/comparisons` | Run selected agents under identical conditions |
| POST | `/api/compare` | Compare saved IDs |
| POST | `/api/training` | Train and persist contextual-bandit values |
| GET | `/api/policy` | Inspect stored route values |
| GET | `/api/mcp` | Tool names and local client configuration |

Example simulation body:

```json
{"agent_id":"goal_based","scenario_id":"rain_urgent","seed":42,"deadline":28,"noise":0}
```

Example comparison body:

```json
{"agent_ids":["simple_reflex","model_based","goal_based","utility_based","learning","hierarchical"],"scenario_id":"rain_urgent","seed":42,"noise":0}
```

Example training body:

```json
{"scenario_id":"rain_urgent","episodes":150,"seed":42,"epsilon":0.2}
```

Example PowerShell:

```powershell
$result = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/api/runs' -ContentType 'application/json' -Body '{"agent_id":"goal_based","scenario_id":"rain_urgent","seed":42}'
$result.metrics
```

Missing run IDs return HTTP 404; invalid request fields return 422. MCP tools report errors using the SDK's standard tool-error response. The saved comparison's `fair_conditions` field checks scenario, seed, deadline override, and route noise; it does not claim statistical equivalence or measure generalization.
