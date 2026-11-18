# UAF-81.95: REAL-TIME IN-ENGINE CO-PILOTING & LIVE SYNCHRONIZATION (UE5 LIVE CO-PILOT FABRIC)

**Status:** Approved & Normative  
**Subsystem:** Universal Asset Framework (AOE/UAF) - Live Synchronization & Editor Co-Piloting  
**Target Engine:** Unreal Engine 5 (EditorActorSubsystem, EditorLevelLibrary, Slate Main Thread, WebSockets/IPC)  
**Execution Environment:** 100% Headless Orchestrator Daemon & In-Editor Python Hook  

---

## 1. MISSION & SCOPE

UAF-81.95 introduces a low-latency, bidirectional co-piloting service linking AOE/UAF's headless generative engine directly to active Unreal Engine 5 Editor viewports. Where previous workflows required manual file transfers, bundle packaging, or editor restarts, UAF-81.95 allows live parameter mutation, terrain sculpting feedback, procedural room regeneration, and squad spawner positioning with response latencies strictly under 500ms.

Crucially, the system protects human designer agency through a deterministic **Designer Lock** concurrency model: manual actor moves inside the Unreal Editor lock the entity from destructive procedural overwriting.

---

## 2. MATHEMATICAL & ARCHITECTURAL SPECIFICATIONS

### 2.1 Communication Topology & Daemon Architecture
The subsystem operates as a non-blocking daemon server (`CoPilotDaemonServer`) communicating over lightweight JSON-RPC sockets / WebSockets (default port `27182`).

```
+---------------------------+       JSON-RPC WebSocket / IPC       +-----------------------------+
|    AOE Headless Daemon    | <==================================> |   UE5 Editor Python Hook    |
|   (aoe-copilot-daemon)    |       (Sub-500ms Delta Frames)       |  (EditorActorSubsystem)     |
+---------------------------+                                      +-----------------------------+
        |                                                                         |
        v                                                                         v
+---------------------------+                                      +-----------------------------+
|    CoPilot Reconciler     |                                      |   Active Viewport Gizmos    |
|   (Designer Lock Wins)    |                                      |  (Human Designer Moves)     |
+---------------------------+                                      +-----------------------------+
```

### 2.2 Coordinate Space Transformation
Position coordinates in AOE adhere to SI metric units (meters, right-handed $Z$-up), whereas Unreal Engine uses centimeters ($1\text{ m} = 100\text{ cm}$):

$$\vec{P}_{\text{UE5}} = 100.0 \cdot \vec{P}_{\text{AOE}}$$
$$\vec{P}_{\text{AOE}} = 0.01 \cdot \vec{P}_{\text{UE5}}$$

Euler rotations map directly: $\text{Pitch}, \text{Yaw}, \text{Roll}$ in degrees.

### 2.3 Live Synchronization Commands
1. `SYNC_TERRAIN_REGION`:
   Transfers a localized bounding-box height delta patch:
   $$\Delta H(x, y) = H_{\text{new}}(x, y) - H_{\text{old}}(x, y)$$
   Allows continuous erosion or road carving adjustments without rebuilding the macro landscape.
2. `SYNC_WFC_ROOMS` & `SYNC_SPAWNER_AI`:
   Spawns, transforms, or despawns modular tiles and NPC squad markers live in the level.
3. `FEEDBACK_TRANSFORM_CHANGED`:
   Viewport gizmo movements by human designers dispatch real-time feedback to AOE, updating the underlying `LevelTopologyGraph` and spatial spawn dictionaries.

### 2.4 Concurrency Arbitration & Designer Lock
When concurrent edits occur, the `CoPilotReconciler` arbitrates according to `ConflictResolutionPolicy`:
- `DESIGNER_LOCK_WINS` (Default): If an actor has been manually transformed by a designer in UE5 (`is_locked_by_designer = True`), procedural regeneration events leave its transform strictly untouched.
- `PROCEDURAL_OVERRIDE`: Explicit command by designer to re-align locked actors to the procedural grid.
- `LATEST_TIMESTAMP`: Wall-clock arbitration for non-conflicting peripheral properties.

### 2.5 Latency Budgets
Every delta synchronization frame satisfies a round-trip time (RTT) constraint:
$$\text{Latency}_{\text{RTT}} \le 500\text{ ms}$$
Guarantees responsive interactive feedback without stuttering the Unreal Editor UI thread.

---

## 3. ACCEPTANCE CRITERIA
- Full session lifecycle transitions (`IDLE` $\to$ `LISTENING` $\to$ `CONNECTED` $\to$ `SYNCING`).
- Zero data loss across JSON-RPC serialization and deserialization cycles.
- Exact unit conversion: $\vec{P}_{\text{UE5}} = 100.0 \cdot \vec{P}_{\text{AOE}}$.
- Successful sub-region terrain patch ingestion and application.
- Designer lock integrity: locked actors preserve manual position against procedural regenerations.
- Latency strictly verified below 500ms budget.
- Zero regressions across the global test suite (> 8,718 tests passing at 100%).
