# Verification

Initial checks on 3 November 2026:

- `python -m pytest -q`: **29 passed**. Tests use separate temporary SQLite files and do not alter the demonstration database.
- `npm run build`: TypeScript compilation and Vite production build passed.
- `npm install`: zero vulnerabilities reported by the dependency audit at install time.
- Production root and `/api/health`: HTTP 200, database connected.
- Baseline initialization: 18 real simulations saved, covering all six agents in three common scenarios.

Automated coverage includes the 18-run lifecycle/metrics matrix, fractional timing, partial-observation memory, reflex independence from previous beliefs, closure failure/recovery, preservation of incurred reroute cost, impossible deadlines, seeded cross-agent route variation, learning persistence and frozen evaluation, API validation/exports, comparison conditions, an actual MCP client/server stdio exchange (discovery, simulation, retrieval, training, comparison, invalid inputs), and a separate real loopback Streamable HTTP server/client exchange.

Browser verification confirmed dashboard rendering, simulation submission and saved outcome, all-six comparison submission, saved-run search, MCP configuration copying, and training through the UI. Browser console inspection found no errors. Fonts are packaged locally, and a production screenshot is saved as `docs/dashboard.png`. The 150-episode urgent-rain training session produced route C as the best learned route; fixed-scenario frozen evaluation changed from 34.5 minutes / 0% on-time to 26.5 minutes / 100% on-time. These are measured educational-model results, not real-world performance estimates.

The installed FastAPI/Starlette test client currently emits an upstream deprecation warning about its httpx test transport; all tests pass. Production API requests do not use that test transport.

This is verification of the implemented bounded educational model. It is not a security audit, a load test, or proof that one agent is best in real-world delivery operations.

## Three.js update · 3 November 2026

- Six frontend geometry/replay tests pass (`npm.cmd test`): endpoints, segment sampling, continuous recorded movement, stationary preparation/seeking, reroute continuity with orthogonal connectors, and display-coordinate conversion.
- TypeScript and Vite production builds pass. Three.js is loaded separately from the dashboard bundle (approximately 146 KB gzipped). Vite reports its standard advisory about the renderer chunk exceeding 500 KB uncompressed.
- Browser checks confirmed the WebGL 3D scene, rain and clear-weather presentation, top-down/follow/orbit camera selection, half-speed playback, restart, and direct seeking to a persisted road-closure reroute event.
- The closure run retained its measured outcome: 22 minutes, 150 fictional cost units, 7.5 km, and route A → C. Rendering does not modify these metrics.
- The backend's 29-test suite and API/MCP behavior are unchanged by this frontend update; the new animation tests are separate.
- Additional design and resource-lifecycle notes: `docs/THREE_JS.md`.
