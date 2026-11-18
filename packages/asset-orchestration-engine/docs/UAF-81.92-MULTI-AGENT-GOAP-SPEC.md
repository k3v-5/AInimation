# UAF-81.92: ADVANCED MULTI-AGENT NPC ECOSYSTEM, COGNITIVE GOAP, SQUAD TACTICS & FACTION REPUTATION (UE5 STATETREE & BEHAVIOR FABRIC)

**Status:** Approved & Normative  
**Subsystem:** Universal Asset Framework (AOE/UAF) - Cognitive AI & Multi-Agent Architecture  
**Target Engine:** Unreal Engine 5 (StateTree, Behavior Trees, AI Controllers, Perception Components)  
**Execution Environment:** 100% Headless Orchestrator & Exporter  

---

## 1. MISSION & SCOPE

UAF-81.92 establishes autonomous, high-level cognitive artificial intelligence for non-player characters (NPCs) and coordinated tactical squads within AOE/UAF. While UAF-81.90 generated interior facility layouts and pacing curves, and UAF-81.91 synthesized macroscopic terrain landscapes and road splines, UAF-81.92 populates these environments with intelligent, reactive, and socially organized agents.

All AI planning, perception, squad communication, and faction reputation mechanics run headlessly without requiring local Unreal Engine installation. The output is a structured export bundle containing **UE5 StateTree** transition schemas, blackboard data assets, squad patrol manifests, and autonomous Unreal Editor Python ingestion scripts.

---

## 2. MATHEMATICAL & ARCHITECTURAL SPECIFICATIONS

### 2.1 WorldState & GOAP Formulation
- **WorldState**: Key-value dictionary representing an agent's beliefs about itself and the world:
  $$S = \{ k_1: v_1, k_2: v_2, \dots, k_n: v_n \} \quad \text{where } v_i \in \{\text{bool, int, float, str}\}$$
- **GOAPAction**:
  - Preconditions: $P \subseteq S$ required for action activation.
  - Effects: $E \subseteq S$ applied upon successful action execution.
  - Operational Cost: $C(a) > 0$.
- **Goal**:
  - Target Conditions: $G \subseteq S$.
  - Priority Weight: $W(g) \ge 0$.
- **State-Space $A^*$ Search**:
  Finds sequence of actions $\pi = \langle a_1, a_2, \dots, a_m \rangle$ minimizing total cost:
  $$J(\pi) = \sum_{i=1}^m C(a_i)$$
  such that $S_0 \xrightarrow{a_1} S_1 \dots \xrightarrow{a_m} S_m$ satisfies $G \subseteq S_m$.

### 2.2 Multi-Agent Squad Tactics & Coordination
Squads coordinate actions over a shared tactical blackboard:
- **Tactical Roles**:
  - `POINTMAN`: Leads advance, breaches locked doors (from UAF-81.90).
  - `SUPPRESSOR`: Lays down high-volume suppression fire, fixing enemy in place.
  - `FLANKER`: Circles around enemy cover using topological corridors or terrain depressions.
  - `SUPPORT_MEDIC`: Administers medical kits, supplies ammunition.
- **Bounding Overwatch (Leapfrogging)**:
  Pairs alternate between movement and static covering fire states.
- **Flanking Geometry**:
  A candidate flanking position $\vec{P}_{\text{flank}}$ relative to target $\vec{P}_{\text{target}}$ and target forward vector $\vec{F}_{\text{target}}$ must satisfy:
  $$\cos(\theta) = \frac{(\vec{P}_{\text{flank}} - \vec{P}_{\text{target}}) \cdot \vec{F}_{\text{target}}}{|\vec{P}_{\text{flank}} - \vec{P}_{\text{target}}|} \le \cos(60^\circ) = 0.5$$
  Guarantees angular separation $\ge 60^\circ$, attacking outside the enemy's front visual arc.

### 2.3 Sensory Perception & Memory Decay
- **Visual Cone**:
  Target $\vec{T}$ is visually perceived from agent position $\vec{A}$ and forward $\vec{F}$ if:
  $$|\vec{T} - \vec{A}| \le R_{\text{vision}} \quad \text{and} \quad \frac{(\vec{T} - \vec{A}) \cdot \vec{F}}{|\vec{T} - \vec{A}|} \ge \cos\left(\frac{\text{FOV}}{2}\right)$$
  subject to non-occluded line-of-sight raycasts.
- **Memory Confidence Decay**:
  Confidence $C(t)$ in a threat's Last Known Position (LKP) decays exponentially over time $t$:
  $$C(t) = C_0 \cdot e^{-\lambda t}$$
  When $C(t) < C_{\text{threshold}}$, threat is declared lost and agent switches to search mode.

### 2.4 Faction Reputation & Alliance Ripple Matrix
- Pairwise disposition $D(F_A, F_B) \in [-100.0, +100.0]$:
  - $\text{Hostile}: D < -30.0$
  - $\text{Neutral}: -30.0 \le D \le +30.0$
  - $\text{Allied}: D > +30.0$
- Alliance Ripple Effect: If faction $F_A$ attacks faction $F_B$, any ally $F_C$ of $F_B$ reduces disposition towards $F_A$:
  $$\Delta D(F_C, F_A) = \Delta D(F_B, F_A) \cdot \frac{D(F_C, F_B)}{100.0}$$

---

## 3. ACCEPTANCE CRITERIA
- 100% deterministic GOAP plan synthesis given the same world state and seed.
- Validated state transitions and automatic replanning on broken preconditions.
- Mathematical verification of flanking angular separation ($\ge 60^\circ$).
- Complete Unreal Engine 5 StateTree & Behavior Tree JSON export bundles.
- Zero regressions across the global test suite.
