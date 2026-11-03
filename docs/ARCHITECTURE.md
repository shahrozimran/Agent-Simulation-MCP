# Architecture

```mermaid
flowchart LR
    U[User] --> UI[React dashboard]
    UI --> API[FastAPI REST API]
    AI[MCP-compatible AI client] --> MCP[MCP server: stdio or Streamable HTTP]
    API --> S[Application service]
    MCP --> S
    S --> E[Bounded seeded simulation]
    E --> A[One selected agent strategy]
    A --> E
    S --> DB[(SQLite: runs, policy, training)]
```

The API and MCP tools call the same service, avoiding divergent simulation logic. The frontend uses API responses for every metric, trace, table, and chart. Map playback replays saved events and never mutates a run. Native Python code executes simulations; an LLM is needed only in an external AI client for conversational control.

## Policy diagrams

### Simple Reflex

```mermaid
flowchart LR
    P[Current traffic observation] --> R[Ordered IF-THEN rules]
    R --> A[Choose default or first non-heavy route]
```

### Model-Based Reflex

```mermaid
flowchart LR
    P[New observation] --> B[Update route beliefs]
    M[Earlier traffic memory] --> B
    B --> R[State-based traffic rules]
    R --> A[Route choice]
```

### Goal-Based

```mermaid
flowchart LR
    M[Nominal route model] --> P[Predict route arrival times]
    G[Delivery deadline] --> F[Find feasible plans]
    P --> F
    F --> C[Cheapest feasible plan or fastest fallback]
```

### Utility-Based

```mermaid
flowchart LR
    P[Predicted time, cost, lateness] --> U[Score time + cost/20 + 4 times lateness]
    U --> A[Choose minimum score]
```

### Learning

```mermaid
flowchart LR
    C[Scenario and objective context] --> V[Saved route reward means]
    V --> A[Choose route]
    A --> E[Delivery environment]
    E --> R[Observed reward]
    R --> T{Explicit training?}
    T -->|Yes| V
    T -->|No| O[Frozen evaluation outcome]
```

### Hierarchical

```mermaid
flowchart TD
    D[Deliver order] --> A[Accept]
    A --> P[Prepare: wait then pick up]
    P --> N[Navigate: fastest route, recover on closure]
    N --> H[Handoff: verify arrival, complete delivery]
```

## Contracts and persistence

Input models reject unknown fields, invalid agent/scenario IDs, negative seeds, invalid deadlines, and unbounded training requests. Responses contain run IDs, configuration, metrics, trace entries, and the policy snapshot used. Trace entries include action, modeled time, lifecycle state, current route/progress, reason, and architecture evidence. MCP summary tools omit bulky traces; `get_run` retrieves the complete trace.

SQLite tables: `runs(id, created_at, batch_id, agent_id, scenario_id, payload)`, `policy(context, route, samples, mean)`, `training(id, created_at, payload)`. JSON payloads preserve the exact configuration and results. Training acquires a writer transaction before reading and updating the policy. Comparisons capture one policy snapshot and use identical pre-generated exogenous route draws for each independent agent.
