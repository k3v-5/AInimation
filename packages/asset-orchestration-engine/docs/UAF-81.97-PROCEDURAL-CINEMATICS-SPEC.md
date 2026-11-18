# UAF-81.97: PROCEDURAL CINEMATICS, CINECAMERA DIRECTOR & UE5 SEQUENCER

**Status:** Approved & Normative  
**Subsystem:** Universal Asset Framework (AOE/UAF) - Procedural Cinematics & In-Engine Sequencer  
**Target Engine:** Unreal Engine 5 (LevelSequence, CineCameraActor, MovieSceneTracks)  
**Execution Environment:** Headless Math Solver & Python Automation Hook  

---

## 1. MISSION & SCOPE

UAF-81.97 provides automated in-engine cinematography, directing dynamic shots, camera movements, focus tracking, and composition for key narrative beats, boss encounters, procedural WFC discovery reveals, and real-time dialogue sequences.

The subsystem replaces static cutscene authoring with algorithmic composition rules (Rule of Thirds, Golden Ratio, OTS, 180° axis compliance), $C^1$-continuous Catmull-Rom spline camera trajectories with collision avoidance against room walls and terrain geometry, and physically accurate depth-of-field optics.

---

## 2. MATHEMATICAL & ARCHITECTURAL FOUNDATIONS

### 2.1 Optical & Framing Mathematics

Let $\vec{P}_{\text{cam}}$ be the camera world position, $\vec{P}_{\text{target}}$ the primary subject position, and $\vec{F} = \frac{\vec{P}_{\text{target}} - \vec{P}_{\text{cam}}}{\|\vec{P}_{\text{target}} - \vec{P}_{\text{cam}}\|}$ the normalized line-of-sight vector.

#### 1. Rule of Thirds & Golden Ratio Framing Offsets
To place the primary subject at normalized screen coordinates $(u, v)$ where $u \in \{1/3, 2/3\}$ or $u \in \{1 - 1/\phi, 1/\phi\} \approx \{0.382, 0.618\}$:
Let $\vec{R} = \vec{F} \times \vec{Z}_{\text{up}}$ be the camera right vector.
The camera look-at aim point $\vec{P}_{\text{aim}}$ is offset from $\vec{P}_{\text{target}}$:
$$\vec{P}_{\text{aim}} = \vec{P}_{\text{target}} + (0.5 - u) \cdot 2 \cdot D \cdot \tan\left(\frac{\text{FOV}_h}{2}\right) \cdot \vec{R}$$
where $D = \|\vec{P}_{\text{target}} - \vec{P}_{\text{cam}}\|$ is the subject distance and $\text{FOV}_h$ is the horizontal field of view.

#### 2. The 180-Degree Conversational Axis Rule
Given two interlocutors $A$ and $B$, the conversation axis is defined by unit vector:
$$\vec{u}_{AB} = \frac{\vec{P}_B - \vec{P}_A}{\|\vec{P}_B - \vec{P}_A\|}$$
The action line normal in the $XY$ plane is $\vec{n}_{AB} = (-u_{AB, y}, u_{AB, x}, 0)$.
All camera positions $\vec{P}_{\text{cam}}$ across alternating shot-reverse-shot pairs must satisfy:
$$\text{sgn}\left( (\vec{P}_{\text{cam}} - \vec{P}_A) \cdot \vec{n}_{AB} \right) = \text{const}$$
guaranteeing that the camera never crosses the 180° line, preserving viewer orientation.

### 2.2 Catmull-Rom Spline Trajectories with Obstacle Avoidance
For control points $\vec{C}_0, \vec{C}_1, \vec{C}_2, \vec{C}_3$ and local time $t \in [0, 1]$:
$$\vec{P}(t) = \frac{1}{2} \left[ 2 \vec{C}_1 + (-\vec{C}_0 + \vec{C}_2) t + (2 \vec{C}_0 - 5 \vec{C}_1 + 4 \vec{C}_2 - \vec{C}_3) t^2 + (-\vec{C}_0 + 3 \vec{C}_1 - 3 \vec{C}_2 + \vec{C}_3) t^3 \right]$$

To avoid clipping through geometry (WFC bounding boxes and terrain elevation $H(x, y)$), the trajectory solver samples the curve at interval $\Delta t$, computes the distance to the nearest static boundary, and applies a repulsive outward potential if distance $< d_{\text{safe}}$ (default $0.5\text{ m}$).

### 2.3 Physical Optics, Circle of Confusion & Hyperfocal Distance
Given focal length $f$ (mm), f-stop $N$, and sensor circle of confusion limit $c \approx 0.03\text{ mm}$:
$$H = \frac{f^2}{N \cdot c} + f$$
The near focus limit $D_{\text{near}}$ and far focus limit $D_{\text{far}}$ for subject distance $D$ are:
$$D_{\text{near}} = \frac{H \cdot D}{H + (D - f)}, \quad D_{\text{far}} = \frac{H \cdot D}{H - (D - f)}$$
The depth of field is:
$$\text{DoF} = D_{\text{far}} - D_{\text{near}}$$

---

## 3. COMPONENT TOPOLOGY

```
src/uaf/cinematics/
├── core/
│   ├── __init__.py
│   └── contracts.py                 # Pydantic schemas, lens settings, shot specs
├── framing/
│   ├── __init__.py
│   └── framing_engine.py            # Rule of Thirds, Golden Ratio, OTS, 180° axis
├── trajectory/
│   ├── __init__.py
│   └── spline_solver.py             # Catmull-Rom splines & collision avoidance
├── focus/
│   ├── __init__.py
│   └── depth_of_field.py            # Dynamic DoF, autofocus, hyperfocal optics
└── exporter/
    ├── __init__.py
    └── ue5_sequencer_exporter.py    # LevelSequence JSON manifest builder for UE5
```
