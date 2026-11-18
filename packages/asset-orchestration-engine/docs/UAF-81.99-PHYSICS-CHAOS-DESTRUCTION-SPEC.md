# UAF-81.99: PHYSICS, VORONOI FRACTURING & CHAOS DESTRUCTION SYSTEM

**Status:** Approved & Normative  
**Subsystem:** Universal Asset Framework (AOE/UAF) - Chaos Physics & Procedural Fracturing  
**Target Engine:** Unreal Engine 5 (Chaos Destruction, GeometryCollection, Niagara VFX)  
**Execution Environment:** Headless Tessellation Solver & Chaos Compiler  

---

## 1. MISSION & SCOPE

UAF-81.99 provides an automated, volumetric physical fracturing engine that transforms static modular building assets (WFC walls, concrete pillars, metallic doors, glass panels) into physically simulated `GeometryCollection` assets for Unreal Engine 5 Chaos Physics.

The subsystem replaces static pre-fractured assets with procedural Voronoi partitioning, hierarchical clustering (Root -> Macro Chunks -> Micro Debris), physical mass and damage threshold assignment, Anchor Fields to preserve structural stability, and reactive Niagara debris/dust emitter presets.

---

## 2. MATHEMATICAL & ARCHITECTURAL FOUNDATIONS

### 2.1 3D Voronoi Tessellation & Radial Impact Clustering
Given a bounding volume $\mathcal{B} = [X_{\min}, X_{\max}] \times [Y_{\min}, Y_{\max}] \times [Z_{\min}, Z_{\max}]$ and a set of seed sites $S = \{ \vec{s}_1, \vec{s}_2, \dots, \vec{s}_n \}$:
The Voronoi cell $V_i$ corresponding to site $\vec{s}_i$ is the convex polyhedron:
$$V_i = \{ \vec{p} \in \mathcal{B} \mid \|\vec{p} - \vec{s}_i\| \le \|\vec{p} - \vec{s}_j\|, \forall j \ne i \}$$

For localized ballistic or explosive impacts at $\vec{P}_{\text{impact}}$, sites are distributed with exponential radial density:
$$\rho(r) = \rho_0 \cdot e^{-k \cdot r}$$
where $r = \|\vec{s} - \vec{P}_{\text{impact}}\|$ is distance to the epicenter, generating fine micro-debris near the blast and preserving larger macro-chunks at the periphery.

### 2.2 Hierarchical Clustering & Connectivity Graph
The Geometry Collection organizes fragments into a 3-tier hierarchy:
- **Level 0 (Root)**: The composite un-fractured asset.
- **Level 1 (Macro Chunks)**: Primary structural fragments that separate under medium strain.
- **Level 2 (Micro Debris)**: Fine debris, concrete splinters, and dust-generating shards that detach under high strain.

Two adjacent cells $V_i, V_j$ share an interface polygon $F_{ij} = V_i \cap V_j$. The structural bond strength is proportional to contact area:
$$S_{ij} = \text{Area}(F_{ij}) \cdot \sigma_{\text{bond}}$$

### 2.3 Physical Mass, Materials & Anchor Fields
Given piece volume $V_{\text{piece}}$ and material density $\rho_{\text{mat}}$:
$$\text{Mass} = V_{\text{piece}} \cdot \rho_{\text{mat}}$$
Standard material densities:
- `CONCRETE`: $2400.0\text{ kg/m}^3$
- `MASONRY_BRICK`: $1900.0\text{ kg/m}^3$
- `REINFORCED_METAL`: $7850.0\text{ kg/m}^3$
- `TEMPERED_GLASS`: $2500.0\text{ kg/m}^3$
- `STRUCTURAL_WOOD`: $650.0\text{ kg/m}^3$

**Anchor Fields**:
To prevent entire buildings from collapsing under quiescent gravity:
$$\text{IsAnchored}(V_i) = \begin{cases} 
\text{True} & \text{if } \vec{C}_i \in \mathcal{B}_{\text{anchor}} \\ 
\text{False} & \text{otherwise} 
\end{cases}$$
where $\vec{C}_i$ is the cell centroid and $\mathcal{B}_{\text{anchor}}$ is the spatial volume of the foundation or structural anchor.

### 2.4 Debris Kinetic Impulse & Niagara Dispersion
When broken by kinetic energy $E_{\text{impact}}$:
$$\vec{v}_{\text{debris}} = \sqrt{\frac{2 \cdot E_{\text{effective}}}{\text{Mass}}} \cdot \frac{\vec{C}_i - \vec{P}_{\text{impact}}}{\|\vec{C}_i - \vec{P}_{\text{impact}}\|} + \vec{v}_{\text{turbulence}}$$

---

## 3. COMPONENT TOPOLOGY

```
src/uaf/chaos_destruction/
├── core/
│   ├── __init__.py
│   └── contracts.py                 # Enums, bounding boxes, fractured pieces, collections
├── fracture/
│   ├── __init__.py
│   └── voronoi_engine.py            # 3D Voronoi sites, radial clustering, cell partitioning
├── compiler/
│   ├── __init__.py
│   └── chaos_compiler.py            # Physics mass calculation, anchor fields, damage thresholds
├── debris/
│   ├── __init__.py
│   └── debris_emitter.py            # Kinetic blast impulses and Niagara emitter presets
└── export/
    ├── __init__.py
    └── ue5_chaos_exporter.py        # GeometryCollection JSON manifests and editor Python hook
```
