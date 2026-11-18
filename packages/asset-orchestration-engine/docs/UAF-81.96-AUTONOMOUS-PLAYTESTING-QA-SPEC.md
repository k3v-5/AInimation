# UAF-81.96: AUTONOMOUS GAMEPLAY PLAYTESTING & AI QA SIMULATION (HEADLESS PLAYTESTING FABRIC)

**Status:** Approved & Normative  
**Subsystem:** Universal Asset Framework (AOE/UAF) - Autonomous Gameplay Testing & AI QA Simulation  
**Target Engines:** Unreal Engine 5, Headless Orchestrator Daemon, CI/CD Automated Validation  
**Execution Mode:** 100% Headless Multi-Agent Discrete-Event Simulation  

---

## 1. MISSION & SCOPE

UAF-81.96 establishes a high-throughput, automated simulation fabric capable of running thousands of synthetic gameplay sessions in headless mode across procedurally generated WFC interiors and macro-landscapes.

The subsystem replaces slow, error-prone manual playtesting with autonomous AI agents that emulate distinct human player profiles, detect critical design flaws (softlocks, unreachable keys, one-way drops, missing nav links), flag unfair combat encounters (difficulty spikes, player TTK under 1.5s), map spatial telemetry heatmaps (deaths, ammo consumption, dwell time), and feed actionable correction vectors back into the level pacing systems in closed loop.

---

## 2. MATHEMATICAL & ARCHITECTURAL FOUNDATIONS

### 2.1 Player Archetypes & Stochastic Behavior Modeling
Agents operate under behavioral utility functions tailored to distinct playstyles:
- **`EXPLORER`**: Prioritizes unvisited rooms and side branches; high tolerance for dwell time, inspects environmental secrets.
- **`SPEEDRUNNER`**: Computes shortest topological distance to primary objectives using Dijkstra/A*; avoids non-mandatory encounters and ignores optional loot.
- **`COMBATANT`**: Aggressive threat engagement; seeks out enemy squads, higher accuracy and combat confidence, accepts higher damage trade-offs.
- **`NOVICE`**: Lower combat accuracy ($acc \in [0.45, 0.65]$), slower reaction time ($t_{\text{react}} \ge 0.5\text{ s}$), higher damage taken, susceptible to resource starvation.
- **`COMPLETIONIST`**: Exhaustive search; will not exit until 100% of collectible items, terminals, and accessible rooms are resolved.

### 2.2 Combat & Survival Differential Simulation
In tick-based discrete simulation, combat exchanges between an agent and an enemy squad $E$ in room $R$ follow:

$$\text{DPS}_{\text{agent}} = \text{WeaponDamage} \cdot \text{FireRate} \cdot \text{Accuracy}_{\text{archetype}}$$
$$\text{DPS}_{\text{squad}} = \sum_{e \in E} \text{EnemyDamage}_e \cdot \text{FireRate}_e \cdot (1.0 - \text{Evasion}_{\text{agent}})$$
$$\text{TTK}_{\text{player}} = \frac{\text{Health}_{\text{agent}} + \text{Shield}_{\text{agent}}}{\text{DPS}_{\text{squad}}}$$
$$\text{TTK}_{\text{enemies}} = \frac{\sum_{e \in E} \text{Health}_e}{\text{DPS}_{\text{agent}}}$$

A **Difficulty Spike** is mathematically flagged when:
$$\text{TTK}_{\text{player}} < 1.5\text{ s} \quad \lor \quad P(\text{Victory}) < 0.20$$
or when the player runs completely out of ammunition in a room with mandatory locking doors ($E_{\text{mandatory}} > 0 \land \text{Ammo} = 0$).

### 2.3 Topological Reachability & Softlock Taxonomy
Let $G = (V, E)$ be the directed room graph where each edge $e = (u, v)$ may have an unlocking condition $C(e)$ (e.g. required key ID $k$).
The reachable set of rooms $\mathcal{R}(t)$ expands monotonically as keys are acquired:
$$\mathcal{K}(t) = \mathcal{K}(t-1) \cup \{ k \in \text{Items}(v) \mid v \in \mathcal{R}(t) \}$$
$$\mathcal{R}(t) = \mathcal{R}(t-1) \cup \{ v \mid (u, v) \in E, u \in \mathcal{R}(t-1), C(u, v) \subseteq \mathcal{K}(t) \}$$

A **Fatal Softlock** occurs if:
$$\text{GoalRoom} \notin \lim_{t \to \infty} \mathcal{R}(t)$$
Types:
1. **`KEY_BEHIND_LOCKED_DOOR`**: Key $k$ required to open door $(u, v)$ is located in a room $w$ reachable only via $(u, v)$.
2. **`DISCONNECTED_ROOM`**: Room $v$ has in-degree 0 or is topologically isolated from start node.
3. **`ONE_WAY_TRAP`**: Directed edge $(u, v)$ with no backward path to $u$ and no reachable forward path to $\text{GoalRoom}$.
4. **`RESOURCE_EXHAUSTION_BLOCK`**: Mandatory combat encounter requires ammo $> \text{AvailableAmmo}_{\text{total}}$.

### 2.4 Spatial Heatmap Grid Binning
The game world bounding volume $[X_{\min}, X_{\max}] \times [Y_{\min}, Y_{\max}]$ is discretized into regular cells of dimension $s_c$ (default $2.0\text{ m}$):
$$\text{cell}_x = \left\lfloor \frac{x - X_{\min}}{s_c} \right\rfloor, \quad \text{cell}_y = \left\lfloor \frac{y - Y_{\min}}{s_c} \right\rfloor$$

For any telemetry metric $M \in \{\text{Deaths}, \text{Ammo}, \text{DwellTime}, \text{DamageTaken}\}$, the raw cell count $C(i, j)$ undergoes 2D discrete Gaussian approximation:
$$\tilde{C}(i, j) = \sum_{di=-1}^{1} \sum_{dj=-1}^{1} K(di, dj) \cdot C(i+di, j+dj)$$
where $K$ is a normalized $3 \times 3$ kernel $\frac{1}{16} \begin{bmatrix} 1 & 2 & 1 \\ 2 & 4 & 2 \\ 1 & 2 & 1 \end{bmatrix}$.
The final heatmap value is normalized to $[0.0, 1.0]$.

### 2.5 Closed-Loop Auto-Calibrator
When the simulation suite fails target quality criteria (e.g. survival rate $< 75\%$ or fatal softlocks found), the `ClosedLoopPacingCalibrator` computes a deterministic repair prescription:
- **Softlock Remediation**: Relocates trapped keys to parent or sibling rooms in $\mathcal{R}(t_{\text{pre-lock}})$.
- **Difficulty Smoothing**: If a room experiences death density $> 40\%$, adjusts enemy spawn count by dampening factor $\delta = \max(0.5, 1.0 - (\text{DeathRate} - 0.25))$, and injects a health/ammo pickup cache in the immediate predecessor room.

---

## 3. COMPONENT TOPOLOGY

```
src/uaf/playtesting/
├── core/
│   ├── __init__.py
│   └── contracts.py             # Domain models, enums, telemetry events & schemas
├── agent/
│   ├── __init__.py
│   └── headless_agent.py        # Autonomous discrete-event player simulator
├── telemetry/
│   ├── __init__.py
│   └── heatmap_generator.py     # 2D/3D grid binning, smoothing & hotspot detection
├── analysis/
│   ├── __init__.py
│   └── softlock_detector.py     # Graph reachability, softlocks & difficulty analyzer
├── pacing/
│   ├── __init__.py
│   └── closed_loop_calibrator.py# Automated tuning vector generator
└── export/
    ├── __init__.py
    └── qa_report_exporter.py    # Multi-format report builder (JSON, MD, CSV)
```
