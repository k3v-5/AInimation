# UAF-81.98: PROCEDURAL QUEST GRAPH, BRANCHING NARRATIVE & DIALOGUE TREES

**Status:** Approved & Normative  
**Subsystem:** Universal Asset Framework (AOE/UAF) - Procedural Narrative & Quest Generation  
**Target Engine:** Unreal Engine 5 (CommonUI, UDataTable, Gameplay Ability System, Faction Systems)  
**Execution Environment:** Headless Narrative Compiler & World State Graph Engine  

---

## 1. MISSION & SCOPE

UAF-81.98 establishes a procedural narrative and branching quest generation architecture that weaves story objectives, moral dilemmas, faction politics, and interactive dialogue trees into coherent Directed Acyclic Graphs (DAGs).

The subsystem connects the modular interior spaces (UAF-81.90), faction dynamics (UAF-81.92), and economy (UAF-81.93) with player agency, ensuring meaningful choices where siding with one faction triggers mutually exclusive narrative branches, alters dialogue options via skill checks, and persists atomic world state flags across gameplay sessions.

---

## 2. MATHEMATICAL & ARCHITECTURAL FOUNDATIONS

### 2.1 Branching Narrative DAG & Topological Resolution
Let $G = (V, E)$ be a directed graph of quest nodes and narrative milestones, where each directed edge $e = (u, v)$ signifies that completing milestone $u$ is a prerequisite for beginning milestone $v$.

#### 1. Acyclicity & Topological Sort (Kahn's Algorithm)
To guarantee that a narrative cannot softlock into circular prerequisite dependencies:
$$\text{InDegree}(v) = |\{ u \in V \mid (u, v) \in E \}|$$
The graph $G$ must admit a topological sort $\sigma = (v_1, v_2, \dots, v_n)$ such that:
$$\forall (u, v) \in E, \quad \sigma^{-1}(u) < \sigma^{-1}(v)$$
If $\exists$ a cycle, the compiler rejects the specification with `ERR_NARRATIVE_CYCLE_DETECTED`.

#### 2. Mutually Exclusive Faction Branches
Let $F_A$ and $F_B$ be opposing factions. If a quest choice commits to faction $F_A$ along branch $B_A \subset V$, any conflicting branch $B_B \subset V$ is marked as mutually exclusive:
$$\forall v \in B_B, \quad \text{State}(v) \leftarrow \text{ABANDONED} \lor \text{FAILED}$$
$$\text{Reputation}(F_A) \leftarrow \text{Reputation}(F_A) + \Delta R_A$$
$$\text{Reputation}(F_B) \leftarrow \text{Reputation}(F_B) - \Delta R_B$$

### 2.2 Dialogue Choice Prerequisite & Skill Check Formulation
Each dialogue choice $C$ has a set of prerequisite conditions $P$ and an optional skill check $S$:
$$P = \{ (k_i, \text{op}_i, \text{val}_i) \}$$
Valid choice eligibility requires all prerequisites to evaluate to true under current world state $\mathcal{W}$:
$$\text{IsEligible}(C, \mathcal{W}) = \bigwedge_{p \in P} \text{Evaluate}(p, \mathcal{W})$$

For skill checks with player attribute level $L_{\text{attr}}$ and difficulty threshold $D_{\text{check}}$:
$$P(\text{Success}) = \frac{L_{\text{attr}}}{L_{\text{attr}} + D_{\text{check}}}$$
In deterministic mode:
$$\text{Success} \iff L_{\text{attr}} \ge D_{\text{check}}$$

### 2.3 World State Transactional Registry
The world state $\mathcal{W}$ consists of:
1. Boolean flags: $\{ \text{flag\_id} \to \text{bool} \}$
2. Integer counters: $\{ \text{counter\_id} \to \text{int} \}$
3. Faction reputation scores: $\{ \text{faction\_id} \to r \in [-100.0, +100.0] \}$
4. Player inventory items: $\{ \text{item\_id} \}$

Mutations to $\mathcal{W}$ are transactional and support atomic rollback snapshots.

---

## 3. COMPONENT TOPOLOGY

```
src/uaf/narrative/
├── core/
│   ├── __init__.py
│   └── contracts.py                 # Enums, quest specs, dialogue nodes, prerequisites
├── graph/
│   ├── __init__.py
│   └── narrative_dag.py             # DAG acyclicity validation, topological sorting
├── dialogue/
│   ├── __init__.py
│   └── dialogue_compiler.py         # Conversation compiler, skill check resolver
├── state/
│   ├── __init__.py
│   └── world_state.py               # WorldStateFlagRegistry with snapshot & rollback
└── export/
    ├── __init__.py
    └── ue5_narrative_exporter.py    # UDataTable CSV/JSON exporter for CommonUI
```
