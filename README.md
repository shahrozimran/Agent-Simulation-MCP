# Agent Simulation Lab · MCP

A working local application with a React frontend, FastAPI backend, SQLite persistence, and an MCP server. Six independent agent architectures control their own fictional food-delivery simulations. The dashboard and MCP server share the same simulation engine and database.

## Start the application

Dependencies and the production frontend have already been installed/built in this folder. **Double-click `Start.cmd`**, or run:

```powershell
Set-Location 'D:\Desktop\Projects\Agent Simulation MCP'
.\Start.ps1
```

Open **http://127.0.0.1:8000**. API documentation: **http://127.0.0.1:8000/docs**. Keep the terminal open; Ctrl+C stops the server. If port 8000 is in use, run `.\Start.ps1 -Port 8010`. The API and built frontend use the same port.

For a hidden background server, use `.\Start-Background.ps1`; stop it with `.\Stop.ps1`. Both accept `-Port`. Background logs are written under `logs/`. `Stop.ps1` checks the process command line and refuses to stop an unrelated application.

If PowerShell blocks a local script, run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Start.ps1` or use `Start.cmd`; no permanent execution-policy change is needed.

## What do I need? Is an LLM API required?

| Component | Required? | Status / purpose |
|---|---|---|
| Python 3.11+ | Yes | Tested here with Python 3.14.5; isolated `.venv` installed |
| Node.js 22.12+ or 24 LTS | For frontend development/builds | Tested here with Node 24.15.0 |
| Database server | No | SQLite creates `data/simulation.sqlite3` automatically |
| LLM API key | No for dashboard, simulator, API, and MCP server | Agent policies are implemented algorithms |
| MCP-compatible AI client | Only for natural-language control | The client supplies model access, using its own subscription, local model, or provider API |
| OpenAI / Anthropic / other provider key | Optional | Only needed if your chosen client/provider requires one |
| GPU, maps API, cloud hosting | No | Fictional map; calculations run locally on CPU |

There is **no built-in LLM chat box** in this version. Use the fully functional dashboard directly, or attach an AI client to the MCP server. No secrets need to be entered into the app. Once dependencies are installed, the application works offline; frontend fonts are bundled locally.

## Features

- Configure a scenario, one or more agents, seed, deadline, and bounded route variation.
- Explore a Three.js 3D city with animated delivery replay, weather, traffic, buildings, trees, river, and bridges.
- Orbit, pan, zoom, switch to a top-down camera, or follow the delivery van. Replay at 0.5×, 1×, 2×, or 4×.
- Compare all six agents under the same pre-generated route conditions.
- Search up to the latest 500 runs; paginated history remains available through the API.
- Export each run as complete JSON or summary CSV.
- Train a contextual bandit with epsilon-greedy exploration and persistent route reward estimates.
- Inspect before/after evaluation and a reward curve from real training episodes.
- Access eight tools over MCP stdio or loopback Streamable HTTP.
- Eighteen measured baseline runs are initialized by the setup script only when the database is empty.

## MCP connection

The dashboard's **MCP connection** screen contains the exact JSON configuration and tool list. A portable example for clients using `mcpServers`:

```json
{
  "mcpServers": {
    "agent-simulation": {
      "command": "D:\\Desktop\\Projects\\Agent Simulation MCP\\.venv\\Scripts\\python.exe",
      "args": ["D:\\Desktop\\Projects\\Agent Simulation MCP\\mcp_server.py"]
    }
  }
}
```

This configuration uses absolute paths and works regardless of the client's current directory. The client launches the server. The dashboard does not need to be running for stdio tools to work, and the MCP server does not need to be running to use the dashboard. Both use the same SQLite file. Refresh the dashboard after experiments created by an external client.

Clients differ in configuration format; adapt the command and arguments to your client's settings. The supplied JSON is not automatically installed in any client's global configuration.

For local HTTP:

```powershell
.\.venv\Scripts\python.exe mcp_server.py --http
```

Connect to `http://127.0.0.1:8001/mcp` with Streamable HTTP. The HTTP MCP server is a separate process from the API on port 8000. It binds to loopback and has no public-deployment authentication configured.

| Tool | Behavior |
|---|---|
| `list_agents` | Discover six architectures and IDs |
| `list_scenarios` | Discover fixtures and defaults |
| `run_simulation` | Run one agent and save its result |
| `run_comparison` | Run all six and return ranked summaries |
| `get_run` | Retrieve full metrics, trace, and decision evidence |
| `list_runs` | Paginated saved summaries |
| `compare_runs` | Compare 2–100 saved results; flag differing conditions |
| `train_learning` | Explicitly update and persist learning route values |

Example prompts:

- “Compare all six agents in `rain_urgent` with seed 42. Explain why the reflex and goal-based choices differ.”
- “Run the model-based and reflex agents in `partial_visibility` and inspect their route-selection evidence.”
- “Train the learning agent for 150 episodes in `rain_urgent`, then run it again and compare its outcome.”
- “Run `road_closure` with the goal-based agent and explain the reroute and its extra cost.”

The project intentionally uses and pins the tested **MCP Python SDK v1 maintenance API** (`FastMCP`, currently installed as `mcp==1.30.0`). Do not mix examples from SDK v2 into this code without a migration. See the [v1 SDK documentation](https://py.sdk.modelcontextprotocol.io/v1/).

## Interactive 3D simulation

The main delivery panel uses Three.js with locally generated geometry and no remote 3D assets. Drag to orbit, scroll to zoom, and right-drag to pan. Use **Top view**, **Follow van**, or the reset-camera button to change perspective. Click a colored route ribbon to inspect it; **Clear** returns highlighting to the agent's current route. Route inspection changes the visual highlight only, not the agent's decision.

The green delivery van follows saved route-progress events, interpolating smoothly between recorded movement steps. Play/pause, seeking, restart, and playback speed control the replay. Restaurant preparation holds the van at pickup; delivery ends at the customer. Road closures show a barrier at the recorded time, and alternate legs are visually anchored at the emergency junction. This is display geometry; saved simulated distance, time, and cost remain authoritative.

Rain/clouds are shown for the rain scenario. Small background cars, water ripples, route light beads, and the arrival pulse are decorative animations and do not represent additional agent runs or change metrics. Ambient car speeds reflect the scenario's traffic multipliers. The **saved run's** scenario drives the displayed world; changing setup takes effect in the next run.

Three.js loads in a separate chunk. Canvas resolution is capped, the scene pauses rendering when off screen or the document is hidden, and geometry/materials/textures and event handlers are released when leaving the simulation page. Reduced-motion settings disable decorative motion and smooth interpolation. If WebGL is unavailable or its context is lost, the existing route map remains available with a visible fallback message.

Frontend geometry/replay checks: run `npm.cmd test` in `frontend` (tested on Node 24).

## Clean setup and development

From the project folder:

```powershell
.\Setup.ps1
.\.venv\Scripts\python.exe -m pytest -q
.\Start.ps1
```

`Setup.ps1` creates the virtual environment, installs `requirements-lock.txt`, runs `npm ci`, builds the frontend, and initializes baseline simulations if the database has no runs. The lock file records the tested Windows/Python environment. For another platform/Python version, resolve `requirements.txt` there instead, then verify dependencies and tests. `pywin32` in the lock file is Windows-specific.

For frontend hot reload, use two terminals:

```powershell
# Terminal 1, project root
.\.venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2
Set-Location frontend
npm.cmd run dev
```

Vite serves `http://127.0.0.1:5173` and proxies `/api` to the backend. After frontend changes, rebuild with `npm.cmd run build` inside `frontend`, then restart the production server. `Start.ps1` serves the last production build.

Manual Inspector test:

```powershell
npx.cmd @modelcontextprotocol/inspector .\.venv\Scripts\python.exe mcp_server.py
```

## Simulation model

This is an educational single-order, single-agent model. Comparison creates independent copies; the six agents do not communicate or cooperate.

| Route | Base travel | Distance | Cost |
|---|---:|---:|---:|
| A · Market Street | 10 min | 5 km | 100 units |
| B · Riverside Drive | 16 min | 8 km | 150 units |
| C · Garden Avenue | 12 min | 6 km | 120 units |

Preparation takes 5 minutes; handoff takes 2 minutes. Route time = base travel × traffic × weather × seeded route variation. Final fractional movement steps preserve exact modeled durations. Predictions use nominal route conditions and never read the sampled future travel variation.

Normal traffic multipliers are `[1,1,1]`. Heavy traffic uses `[2.2,1.1,1.3]`. Rain adds a 1.25 multiplier. In the urgent-rain fixture, total predicted durations are 34.5, 29, and 26.5 minutes, with a 28-minute deadline. Costs are fictional units, not real currency.

**Architectures:** reflex uses current-only traffic rules; model-based reflex remembers missing observations; goal-based selects the cheapest deadline-feasible route with fastest fallback; utility minimizes duration + cost/20 + 4×lateness; learning uses a contextual bandit; hierarchy executes prepare, navigate, and handoff subtasks, using fastest-route selection in navigation. Lifecycle validation belongs to the shared environment. Goal/utility/hierarchy use the configured nominal route model.

**Learning:** reward v1 = −(duration + cost/20 + 4×lateness + 200 if delivery fails). Untrained evaluation chooses the first route. Training samples unvisited routes, then explores with epsilon 0.2 or exploits the largest estimated mean reward. Each route mean uses the incremental sample average. Normal runs are frozen and never update the policy. Keys include scenario, deadline, noise, and reward version; the training UI deliberately trains the default-deadline, zero-noise context. Custom deadline/noise runs may therefore remain untrained. The saved 30-seed evaluation has zero noise and demonstrates this fixed scenario, not statistical generalization.

**Closure recovery:** route A closes at minute 8. The fixed reflex policy reports failure. Adaptive policies can switch at a fictional emergency junction; previous travel remains charged, and the alternate leg incurs its full route distance/time/cost. This deliberately simple connector model is recorded in the trace. The map is illustrative, not a geographic routing engine; the 3D view anchors an alternate leg at the junction while retaining the backend's full-leg timing model.

Runs are bounded to 180 simulated minutes and 250 trace actions. All built-in scenarios finish or explicitly fail. See [architecture](docs/ARCHITECTURE.md), [API examples](docs/API.md), and [verification](docs/VERIFICATION.md).

## Data and scope

All times are stored in UTC and displayed in the browser's local timezone. The database path is absolute relative to this project, so API/MCP processes share it regardless of working directory. Override with the `SIMULATION_DB` environment variable for isolated tests or another database location. SQLite WAL and transaction boundaries protect concurrent writers. Training writes route values and its session record in one transaction; comparisons save all runs in one transaction. Back up the SQLite database with SQLite's backup API while running, or copy it after stopping all API/MCP processes.

This is a local application, not a publicly deployed service. No authentication, multi-user access model, live delivery integrations, payments, notifications, or provider-hosted LLM chat is included. Public hosting would require those deployment decisions and an authentication layer.

## Source map

```text
backend/
  catalog.py       Agents, routes, and five scenarios
  models.py        Validated API/MCP input contracts
  engine.py        Seeded simulator and six decision strategies
  storage.py       SQLite schema, persistence, summaries
  service.py       Shared simulation, comparisons, training
  api.py           FastAPI routes and production frontend hosting
frontend/src/
  main.tsx         React dashboard and playback controls
  DeliveryScene.tsx Three.js city, vehicles, weather, cameras
  sceneMath.ts     Trace-driven animation and route geometry
  styles.css       Responsive visual system
mcp_server.py      Eight MCP tools (stdio / Streamable HTTP)
tests/             Engine, API, and real stdio MCP integration checks
scripts/           One-time measured baseline initialization
data/              Local database (excluded from Git)
```
#   A g e n t - S i m u l a t i o n - M C P  
 