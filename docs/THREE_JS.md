# Three.js delivery world

The frontend uses locally installed `three` and its OrbitControls addon. The existing Python API, MCP tools, SQLite persistence, and six agent algorithms remain the simulation source of truth.

Files:

- `frontend/src/DeliveryScene.tsx`: scene, procedural buildings, vehicles, road ribbons, river, bridges, parks, rain particles, clouds, cameras, route inspection, lifecycle cleanup, and animation loop.
- `frontend/src/sceneMath.ts`: renderer-independent path sampling, route geometry, movement interpolation, and continuous reroute anchoring.
- `frontend/tests/sceneMath.test.ts`: six Node tests for endpoints, segment traversal, recorded movement interpolation, stationary preparation, seeking, reroute continuity, and coordinate conversion.

The van is the agent-controlled delivery vehicle. Small background cars and environmental animations are decorative. The view does not simulate additional deliveries, alter stored metrics, or call an LLM.

The visual interpolation uses the current trace step and its next recorded MOVE event. Pausing freezes the interpolation phase; seeking or restarting resets it to the selected trace state. Reroute legs begin at the prior recorded closure position. Geometry remains an illustrative projection of the bounded backend model rather than a geographic map.

Interaction: drag to orbit; right-drag to pan; scroll to zoom; choose top-down or following cameras; reset to the initial city overview. Click a route ribbon to inspect it. Replay speeds are 0.5×, 1×, 2×, and 4×. Browser reduced-motion preferences stop ambient animations and use discrete recorded positions.

Three.js is lazy-loaded in a dedicated frontend chunk. Pixel ratio is capped at 1.75, rain is drawn as one line-segment batch, offscreen/background rendering is suspended, and resources/event listeners are disposed on unmount. The SVG map is kept as an explicit WebGL-unavailable/context-loss fallback. A missing WebGL implementation is reported in the UI.

Validation commands:

```powershell
Set-Location 'D:\Desktop\Projects\Agent Simulation MCP\frontend'
npm.cmd test
npm.cmd run build
```

Implementation references: [Three.js scene setup](https://threejs.org/manual/pages/creating-a-scene.html), [OrbitControls](https://threejs.org/docs/pages/OrbitControls), and [renderer lifecycle](https://threejs.org/docs/pages/WebGLRenderer).
