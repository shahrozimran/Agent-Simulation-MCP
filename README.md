# Agent Simulation Lab — Multi-Agent Architecture Simulator with MCP

> An interactive AI agent simulation platform featuring six intelligent agent architectures, a Three.js 3D delivery environment, real-time visualization of recorded simulations, FastAPI services, SQLite persistence, and Model Context Protocol (MCP) integration.

## Project Overview

**Agent Simulation Lab** is a locally hosted simulation and experimentation platform designed to demonstrate the behavior, decision-making processes, and performance of six artificial intelligence agent architectures in a fictional food-delivery environment.

The project combines a **React frontend**, a **Three.js 3D city visualization**, a **FastAPI backend**, an **SQLite database**, and an **MCP server**. All components use a shared simulation engine, allowing simulations to be executed through the graphical dashboard, REST API, or MCP-compatible AI clients.

The platform supports reproducible experiments, scenario-based comparisons, decision trace inspection, learning-agent training, persistent simulation history, and interactive replay.

The six agents are independently evaluated under equivalent conditions. They do not communicate or cooperate in a shared multi-agent environment.

---

## Table of Contents

1. [Key Features](#key-features)
2. [Technology Stack](#technology-stack)
3. [System Architecture](#system-architecture)
4. [AI Agent Architectures](#ai-agent-architectures)
5. [Simulation Environment](#simulation-environment)
6. [Interactive 3D Visualization](#interactive-3d-visualization)
7. [Simulation and Decision-Making Logic](#simulation-and-decision-making-logic)
8. [Learning Agent and Training](#learning-agent-and-training)
9. [MCP Server Integration](#mcp-server-integration)
10. [Installation and Setup](#installation-and-setup)
11. [Running the Application](#running-the-application)
12. [Development and Testing](#development-and-testing)
13. [Database and Persistence](#database-and-persistence)
14. [Project Structure](#project-structure)
15. [Limitations and Scope](#limitations-and-scope)

---

## Key Features

### Six AI Agent Architectures

Explore and compare six agent implementations:

- Simple Reflex Agent
- Model-Based Reflex Agent
- Goal-Based Agent
- Utility-Based Agent
- Learning Agent
- Hierarchical Agent

Each architecture follows its own decision-making strategy and can be evaluated under the same simulated route conditions.

### Interactive Simulation Dashboard

- Configure simulation scenarios and agent selections.
- Set simulation seeds and delivery deadlines.
- Adjust bounded route variation.
- Execute individual agent experiments.
- Compare all six architectures under shared conditions.
- Inspect agent decisions and execution traces.
- Review saved simulation results.

### Three.js 3D City Environment

- Interactive fictional city.
- Animated food-delivery vehicle.
- Buildings, trees, roads, river, and bridges.
- Weather and traffic visualization.
- Route highlighting and inspection.
- Camera orbit, pan, and zoom.
- Top-down and vehicle-following cameras.
- Simulation replay controls.

### Experimentation and Analytics

- Reproducible seeded experiments.
- Six-agent comparative analysis.
- Saved run history.
- Complete JSON export.
- Summary CSV export.
- Contextual-bandit training.
- Learning reward visualization.
- Before-and-after learning evaluation.

### MCP Integration

The project exposes **eight MCP tools** for external AI clients to inspect, execute, compare, and analyze simulations.

---

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Frontend | React | Interactive application interface |
| 3D Visualization | Three.js | Animated city and delivery replay |
| Backend | FastAPI | REST API and simulation services |
| Programming Language | Python | Agent architectures and simulation logic |
| Frontend Tooling | Node.js and Vite | Development and production builds |
| Database | SQLite | Persistent simulation results |
| AI Integration | Model Context Protocol | External AI-client interaction |
| MCP Implementation | FastMCP | MCP server and tool exposure |
| Testing | pytest | Backend and integration verification |

### System Requirements

| Component | Requirement |
|---|---|
| Python | 3.11 or newer |
| Node.js | 22.12+ or Node.js 24 LTS |
| Database server | Not required |
| GPU | Not required |
| External maps API | Not required |
| Cloud hosting | Not required |
| LLM API key | Not required for core simulation |
| MCP AI client | Optional |
| Internet connection | Not required after dependencies are installed |

The supplied environment was tested with Python 3.14.5 and Node.js 24.15.0.

**Important:** The simulator implements agent decision algorithms directly. An OpenAI, Anthropic, or other model-provider API key is only required when a separately configured AI client needs one.

---

## System Architecture

The application includes a React visualization layer, shared backend services, a simulation engine, persistent data storage, and an MCP interface.

```text
                  +-------------------------+
                  |     React Dashboard     |
                  |  Simulation Interface   |
                  +------------+------------+
                               |
                               v
                  +-------------------------+
                  |       FastAPI API       |
                  |   REST API + Services   |
                  +------------+------------+
                               |
                               v
                  +-------------------------+
                  |    Simulation Engine    |
                  |  Agent Decision Logic   |
                  +------------+------------+
                               |
                               v
                  +-------------------------+
                  |     SQLite Database     |
                  | Runs, Results, Training |
                  +------------+------------+
                               ^
                               |
                  +------------+------------+
                  |        MCP Server       |
                  |      Eight Tools        |
                  +------------+------------+
                               ^
                               |
                  +------------+------------+
                  |  External MCP AI Client |
                  +-------------------------+
```

The REST API and MCP server use the same simulation services and database, allowing both interfaces to access saved experiments.

The dashboard and the MCP server can operate independently.

---

## AI Agent Architectures

### 1. Simple Reflex Agent

The Simple Reflex Agent uses current observations and condition-action rules.

**Decision approach:**

- Observes the available traffic conditions.
- Applies its predefined route-selection rules.
- Selects an action based on the current observations.
- Does not maintain a separate memory of earlier observations.

This architecture demonstrates rule-based reactive behavior.

### 2. Model-Based Reflex Agent

The Model-Based Reflex Agent extends reactive behavior with an internal representation of earlier observations.

**Decision approach:**

- Observes the current environment.
- Retains information from previous observations.
- Uses that information when current observations are incomplete.
- Selects a route using its stored model and decision rules.

This architecture is useful for studying partial observability.

### 3. Goal-Based Agent

The Goal-Based Agent selects actions based on a delivery objective.

**Decision approach:**

- Evaluates available routes.
- Predicts route completion times.
- Considers the configured delivery deadline.
- Selects the cheapest route expected to satisfy the deadline.
- Uses the fastest available route as a fallback when no route is predicted to satisfy the deadline.

The architecture emphasizes goal satisfaction rather than fixed reactive rules.

### 4. Utility-Based Agent

The Utility-Based Agent evaluates routes using a numerical objective.

Its route score is:

```text
Utility Cost = Duration + (Cost / 20) + (4 × Lateness)
```

The agent chooses the route with the lowest calculated score.

This allows the agent to balance delivery duration, transportation cost, and lateness.

The numerical weights are part of the project's fictional simulation model.

### 5. Learning Agent

The Learning Agent uses a contextual multi-armed bandit approach to estimate which route performs best in a given simulation context.

Its implementation includes:

- Epsilon-greedy exploration.
- Persistent route reward estimates.
- Route sampling and exploitation.
- Explicit training episodes.
- Before-and-after evaluation.
- Reward curve visualization.

Training occurs only when explicitly requested. Ordinary evaluation runs do not update the learned policy.

### 6. Hierarchical Agent

The Hierarchical Agent organizes delivery execution into subtasks.

Its high-level stages are:

```text
Delivery Task
     |
     +-- Prepare Order
     |
     +-- Navigate to Destination
     |       |
     |       +-- Evaluate Routes
     |       +-- Select Fastest Route
     |
     +-- Complete Handoff
```

This architecture demonstrates task decomposition and staged decision execution.

---

## Simulation Environment

The application uses a fictional food-delivery environment with three predefined delivery routes.

### Available Routes

| Route | Base Travel Time | Distance | Cost |
|---|---:|---:|---:|
| A — Market Street | 10 minutes | 5 km | 100 units |
| B — Riverside Drive | 16 minutes | 8 km | 150 units |
| C — Garden Avenue | 12 minutes | 6 km | 120 units |

### Delivery Process

Each simulation includes:

1. Restaurant preparation.
2. Route selection.
3. Vehicle navigation.
4. Delivery handoff.
5. Result and decision trace persistence.

Restaurant preparation takes **5 simulated minutes**.

Delivery handoff takes **2 simulated minutes**.

### Route Duration Calculation

```text
Route Travel Time =
    Base Travel Time
    × Traffic Multiplier
    × Weather Multiplier
    × Seeded Route Variation
```

Final fractional movement steps preserve the modeled route duration.

Agent predictions use nominal route conditions and cannot inspect the randomly sampled future variation.

### Traffic and Weather

Normal traffic multipliers:

```text
[1.0, 1.0, 1.0]
```

Heavy traffic multipliers:

```text
[2.2, 1.1, 1.3]
```

Rain multiplier:

```text
1.25
```

These values are simulation parameters rather than real-world traffic measurements.

### Urgent Rain Example

For the urgent-rain fixture:

| Route | Predicted Total Duration |
|---|---:|
| A | 34.5 minutes |
| B | 29 minutes |
| C | 26.5 minutes |

**Delivery deadline:** 28 minutes.

This scenario demonstrates how different agent architectures respond to deadlines, route costs, and environmental conditions.

### Road Closure Recovery

The road-closure scenario includes a closure of Route A at simulation minute 8.

- The fixed reflex policy reports failure.
- Adaptive policies may select an alternative route.
- Previously incurred travel costs remain charged.
- The alternate route incurs its full modeled distance, duration, and cost.
- Recovery decisions are saved in the execution trace.

The environment uses an intentionally simplified fictional emergency-junction model. It is not a real geographic routing engine.

---

## Interactive 3D Visualization

The project features a Three.js city visualization generated from local assets and geometry.

### Environment Components

- Buildings and city structures.
- Streets and delivery routes.
- River and bridges.
- Trees and decorative objects.
- Traffic and background vehicles.
- Weather effects.
- Animated delivery van.
- Route ribbons and visual indicators.

### Camera Controls

| Action | Function |
|---|---|
| Left mouse drag | Orbit camera |
| Right mouse drag | Pan camera |
| Mouse wheel | Zoom |
| Top View | Switch to overhead perspective |
| Follow Van | Follow delivery vehicle |
| Reset Camera | Restore default viewpoint |
| Select Route | Highlight and inspect a route |

### Replay Features

The replay system supports:

- Play and pause.
- Timeline seeking.
- Restart.
- 0.5× playback.
- 1× playback.
- 2× playback.
- 4× playback.

The vehicle follows recorded simulation events. Playback changes presentation only; it does not rerun the decision algorithm.

### Visualization Accuracy

The saved simulation results remain authoritative.

Decorative animations such as background traffic, water movement, route lighting, and arrival effects do not modify simulated outcomes.

The visualization also includes performance measures:

- Separately loaded Three.js components.
- Capped canvas resolution.
- Rendering pauses when the scene is hidden.
- Resource cleanup when leaving the simulation page.
- Reduced-motion support.
- Fallback route map when WebGL is unavailable.

---

## Simulation and Decision-Making Logic

The project is an educational, single-agent, single-order simulation model.

Each comparison runs independent copies of the same environment so the agent strategies can be evaluated under shared conditions.

### Experiment Reproducibility

Simulations support:

- Configurable random seed.
- Scenario selection.
- Delivery deadline.
- Bounded travel variation.
- Saved execution traces.
- Persistent results.

Using the same parameters supports repeatable comparisons.

### Simulation Constraints

- Maximum simulated duration: 180 minutes.
- Maximum trace actions: 250.
- Runs finish successfully or report explicit failure.
- Agent choices and simulation results are stored for inspection.

### Comparison Process

```text
Select Scenario and Seed
           |
           v
Generate Shared Conditions
           |
           v
Run Six Independent Agents
           |
           v
Record Decisions and Results
           |
           v
Compare Agent Performance
           |
           v
Save Results to SQLite
```

---

## Learning Agent and Training

The Learning Agent implements contextual-bandit route selection.

### Reward Function

```text
Reward =
  -(Duration
    + Cost / 20
    + 4 × Lateness
    + Failure Penalty)
```

The failure penalty is 200 when the delivery fails and 0 otherwise.

### Training Strategy

During training:

1. Unvisited routes are sampled.
2. The agent explores with an epsilon probability of 0.2.
3. Otherwise, it exploits the route with the highest estimated mean reward.
4. Rewards are recorded after each episode.
5. Route value estimates are updated using an incremental sample average.
6. Learned estimates are persisted in SQLite.

### Training and Evaluation Separation

The simulator separates training from ordinary evaluation.

- Training explicitly changes learned route values.
- Normal simulations do not update those values.
- Untrained evaluation selects the first route.
- Training contexts include scenario, deadline, route noise, and reward version.
- The training interface uses the default deadline and zero-noise context.

The saved evaluation uses 30 seeds and zero noise. Its result represents that specific experimental setting rather than proof of general performance across all environments.

---

## MCP Server Integration

The project supports Model Context Protocol (MCP), allowing compatible AI clients to interact with the simulation tools.

### Supported MCP Transports

1. Standard input/output (stdio).
2. Loopback Streamable HTTP.

The MCP server can execute simulations, inspect agents, retrieve saved results, run comparisons, and train the learning policy.

### Available MCP Tools

| MCP Tool | Function |
|---|---|
| `list_agents` | Discover the six agent architectures and their identifiers |
| `list_scenarios` | Retrieve available scenarios and default settings |
| `run_simulation` | Execute one agent simulation and persist the result |
| `run_comparison` | Execute all six agents under comparable conditions |
| `get_run` | Retrieve complete metrics and execution evidence |
| `list_runs` | Retrieve paginated saved simulation history |
| `compare_runs` | Compare between 2 and 100 saved runs |
| `train_learning` | Train the learning agent and persist its route values |

### Example MCP Configuration

For clients supporting the `mcpServers` configuration format:

```json
{
  "mcpServers": {
    "agent-simulation": {
      "command": "D:\\Desktop\\Projects\\Agent Simulation MCP\\.venv\\Scripts\\python.exe",
      "args": [
        "D:\\Desktop\\Projects\\Agent Simulation MCP\\mcp_server.py"
      ]
    }
  }
}
```

**Note:** Update the paths to match your installation directory. This example uses the original Windows project path.

The MCP client launches the stdio server directly. Running the web dashboard is not required for stdio tool access.

### Streamable HTTP

From the project root:

```powershell
.\.venv\Scripts\python.exe mcp_server.py --http
```

MCP endpoint:

```text
http://127.0.0.1:8001/mcp
```

The MCP HTTP server runs independently of the FastAPI server on port 8000.

It binds to the local loopback interface and is not configured for authenticated public deployment.

### Example AI Client Prompts

**Agent comparison**

> Compare all six agents in rain_urgent with seed 42. Explain why the reflex and goal-based choices differ.

**Partial observability**

> Run the model-based and reflex agents in partial_visibility and inspect their route-selection evidence.

**Learning experiment**

> Train the learning agent for 150 episodes in rain_urgent, then run it again and compare its outcome.

**Road closure analysis**

> Run road_closure with the goal-based agent and explain the reroute and its extra cost.

### MCP SDK Compatibility

The project uses the tested MCP Python SDK v1 maintenance API and FastMCP.

The documented installed SDK version is:

```text
mcp==1.30.0
```

SDK v2 examples should not be mixed into this implementation without a migration.

Reference: https://py.sdk.modelcontextprotocol.io/v1/

---

## Installation and Setup

### Prerequisites

Install:

- Python 3.11 or newer.
- Node.js 22.12+ or 24 LTS.
- Git.
- A modern browser supporting WebGL for the 3D view.

The project does not require a cloud database or a model-provider API key for its core simulation.

### Step 1 — Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

Enter the cloned directory.

```powershell
Set-Location "Agent Simulation MCP"
```

Replace the directory name with your actual cloned folder.

### Step 2 — Run Automated Setup

From PowerShell:

```powershell
.\Setup.ps1
```

The setup script:

1. Creates a Python virtual environment.
2. Installs the pinned Python dependencies.
3. Installs frontend dependencies using npm.
4. Builds the React frontend.
5. Initializes measured baseline simulations if the database contains no runs.

The original Windows environment uses `requirements-lock.txt`.

For another operating system or Python version, dependency resolution may need to use `requirements.txt` instead.

### Step 3 — Start the Application

Double-click:

```text
Start.cmd
```

Alternatively:

```powershell
.\Start.ps1
```

### Step 4 — Open the Dashboard

Application:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs

Both addresses are local to the computer running the application.

---

## Running the Application

### Start on an Alternative Port

If port 8000 is occupied:

```powershell
.\Start.ps1 -Port 8010
```

### Start in the Background

```powershell
.\Start-Background.ps1
```

### Stop the Background Server

```powershell
.\Stop.ps1
```

Background logs are written to the `logs/` directory.

The stopping script validates the target process before terminating it.

### PowerShell Execution Policy

If PowerShell blocks local scripts, use:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Start.ps1
```

Alternatively, run `Start.cmd`.

The bypass applies to the launched process and does not permanently modify the Windows execution policy.

---

## Development and Testing

### Backend Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### Frontend Tests

```powershell
Set-Location frontend
npm.cmd test
```

### Frontend Production Build

```powershell
npm.cmd run build
```

### Backend Development Server

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Development Server

In a second terminal:

```powershell
Set-Location frontend
npm.cmd run dev
```

The Vite development server runs at:

```text
http://127.0.0.1:5173
```

It proxies API calls to the FastAPI backend.

After modifying the frontend, rebuild it before running the production server.

### MCP Inspector

For manually inspecting MCP tools:

```powershell
npx.cmd @modelcontextprotocol/inspector .\.venv\Scripts\python.exe mcp_server.py
```

### Verification

The project documentation refers to:

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Verification Documentation](docs/VERIFICATION.md)

---

## Database and Persistence

SQLite provides local persistence for simulation experiments.

### Database File

```text
data/simulation.sqlite3
```

### Stored Data

The application stores:

- Simulation configurations.
- Agent selections.
- Selected scenarios and seeds.
- Simulation metrics.
- Decision traces.
- Saved comparisons.
- Learning-agent estimates.
- Training sessions and results.

### Database Configuration

The database path is resolved relative to the project so that the API and MCP processes can access the same data.

To override the database location, configure:

```text
SIMULATION_DB
```

### Concurrency and Reliability

The SQLite implementation uses WAL mode and transaction boundaries.

- Concurrent processes can access persisted data.
- Training updates and their session records are saved transactionally.
- Comparative results are stored in a single transaction.
- Tests use isolated databases where configured.

For database backups while the application is running, use SQLite's backup API. Alternatively, stop the API and MCP processes before copying the database file.

---

## Project Structure

```text
Agent Simulation MCP/
|
+-- backend/
|   +-- catalog.py
|   +-- models.py
|   +-- engine.py
|   +-- storage.py
|   +-- service.py
|   +-- api.py
|
+-- frontend/
|   +-- src/
|   |   +-- main.tsx
|   |   +-- DeliveryScene.tsx
|   |   +-- sceneMath.ts
|   |   +-- styles.css
|   |
|   +-- tests/
|
+-- tests/
|
+-- scripts/
|
+-- docs/
|   +-- ARCHITECTURE.md
|   +-- API.md
|   +-- VERIFICATION.md
|
+-- data/
|   +-- simulation.sqlite3
|
+-- mcp_server.py
+-- Setup.ps1
+-- Start.ps1
+-- Start.cmd
+-- Start-Background.ps1
+-- Stop.ps1
+-- requirements.txt
+-- requirements-lock.txt
+-- README.md
```

### Important Modules

| File | Responsibility |
|---|---|
| `backend/catalog.py` | Agent definitions, routes, and simulation scenarios |
| `backend/models.py` | Input validation and data models |
| `backend/engine.py` | Simulation engine and six decision strategies |
| `backend/storage.py` | SQLite storage and result retrieval |
| `backend/service.py` | Shared simulation, comparison, and training operations |
| `backend/api.py` | FastAPI endpoints and frontend hosting |
| `frontend/src/main.tsx` | React dashboard and replay controls |
| `frontend/src/DeliveryScene.tsx` | Three.js visualization |
| `frontend/src/sceneMath.ts` | Trace-driven animation and route geometry |
| `mcp_server.py` | Eight MCP tools |
| `tests/` | Backend and MCP integration tests |

---

## Limitations and Scope

This project is a local educational simulation platform.

### Current Scope

- Fictional food-delivery environment.
- Six independently evaluated agent architectures.
- Reproducible scenario-based experimentation.
- Local simulation and visualization.
- Persistent experiment history.
- MCP access from compatible external clients.

### Current Limitations

- No publicly hosted deployment.
- No built-in user authentication.
- No multi-user access model.
- No real-world delivery or maps integration.
- No payment processing.
- No notification service.
- No built-in provider-hosted LLM chat.
- No communication or cooperation between the six simulated agents.
- No guarantee that simulated performance transfers to real delivery operations.

Public deployment would require additional hosting, security, authentication, and operational decisions.

---

## Educational Purpose

Agent Simulation Lab provides a practical environment for exploring AI agent architectures, decision-making under different environmental conditions, route selection, utility optimization, learning through feedback, experimental reproducibility, and MCP-based tool integration.

It is designed to make agent behavior observable and comparable through structured simulation results and interactive visualization.

---

**Agent Simulation Lab — Built with Python, FastAPI, React, Three.js, SQLite, and Model Context Protocol.**
