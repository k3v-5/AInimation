# UAF-81.91: UNIVERSAL PROCEDURAL MACRO-LANDSCAPE, HYDRAULIC EROSION, BIOME DISTRIBUTION & SPLINE INFRASTRUCTURE (UE5 PCG & LANDSCAPE SUBSTRATE)

**Status:** Approved & Normative  
**Subsystem:** Universal Asset Framework (AOE/UAF) - Macro Landscape & World Generation  
**Target Engine:** Unreal Engine 5 (Landscape, PCG, Spline Components, World Partition)  
**Execution Environment:** 100% Headless Orchestrator & Exporter  

---

## 1. MISSION & SCOPE

UAF-81.91 provides AOE/UAF with autonomous, deterministic, and physically-grounded macro-landscape generation. While UAF-81.90 solved interior modular facilities via Wave Function Collapse (WFC), UAF-81.91 creates the macro-terrains, river drainage basins, road networks, and ecological biomes that connect and house these installations.

All generation runs headlessly without requiring local Unreal Engine installation. The output is a self-contained, binary-compatible export bundle containing 16-bit raw heightmaps (`.r16`), 8-bit material layer weightmaps, spline actor JSON manifests, and autonomous Unreal Editor Python ingestion scripts.

---

## 2. MATHEMATICAL SPECIFICATIONS

### 2.1 Heightfield Representation & Coordinate Space
- Discrete grid of dimensions $W \times L$ (recommended standard Unreal Landscape sizes: $505 \times 505$, $1009 \times 1009$, $2017 \times 2017$).
- Internal normalized elevation: $h(x, y) \in [0.0, 1.0]$.
- Physical elevation in centimeters: $Z_{\text{cm}} = (h(x, y) \cdot H_{\text{range}} - H_{\text{range}} / 2) \cdot 100.0$.
- Unreal 16-bit Raw Format:
  $$\text{RAW}_{16}(x, y) = \text{uint16}\left(\text{clamp}\left(h(x, y) \cdot 65535.0, 0, 65535\right)\right)$$
  Stored as little-endian unsigned 16-bit integers (`<H`).

### 2.2 Particle-Based Hydraulic Erosion
For each simulated water droplet:
1. **Position & Velocity Update**:
   $$\vec{v}_{t+1} = \vec{v}_t + \Delta t \cdot \left(\vec{g}_{\text{gravity}} \cdot \nabla h(x, y) - \mu_{\text{friction}} \cdot \vec{v}_t\right)$$
2. **Sediment Capacity**:
   $$C = K_c \cdot |\vec{v}| \cdot \sin(\theta) \cdot V_{\text{water}}$$
   Where $\theta = \arctan(|\nabla h|)$ is the local terrain slope.
3. **Erosion & Deposition**:
   - If sediment $s < C$: soil is eroded by $E = K_e \cdot (C - s)$ using a bilinear brush radius $R$.
   - If sediment $s > C$: excess sediment is deposited: $D = K_d \cdot (s - C)$.
4. **Evaporation**:
   $$V_{\text{water}, t+1} = V_{\text{water}, t} \cdot (1 - \lambda_{\text{evaporate}})$$

### 2.3 Thermal / Talus Relaxation
Iterates across the terrain matrix:
$$\text{If } \frac{\Delta h}{\Delta x} > \tan(\theta_{\text{talus}}): \quad \Delta h_{\text{transferred}} = \frac{1}{2} \cdot \left(\Delta h - \Delta x \cdot \tan(\theta_{\text{talus}})\right)$$
Transfers material downhill until slope is within the angle of repose ($32^\circ - 36^\circ$).

### 2.4 Whittaker Ecological Climate Model
- **Altitude Lapse Rate**:
  $$T(x, y) = T_{\text{sea\_level}} - 0.0065^\circ\text{C/m} \cdot Z_{\text{m}}(x, y)$$
- **Rain Shadow & Orographic Precipitation**: Moisture increases on windward slopes and diminishes in rain-shadow basins.
- **Biomes**: Classified into Tundra, Alpine, Coniferous Forest, Temperate Forest, Grassland, Desert, and Wetland.

### 2.5 Cost-Surface $A^*$ Road Infrastructure
Connects Points of Interest (POIs) along minimum-energy paths:
$$\text{Cost}(u, v) = \text{Distance}(u, v) \cdot \left(1.0 + \alpha \cdot \text{Slope}^2 + \beta \cdot \text{WaterPenalty}\right)$$
Smoothed using Catmull-Rom cubic splines:
$$\vec{P}(t) = 0.5 \left( (2\vec{P}_1) + (-\vec{P}_0 + \vec{P}_2)t + (2\vec{P}_0 - 5\vec{P}_1 + 4\vec{P}_2 - \vec{P}_3)t^2 + (-\vec{P}_0 + 3\vec{P}_1 - 3\vec{P}_2 + \vec{P}_3)t^3 \right)$$

---

## 3. ACCEPTANCE CRITERIA
- 100% deterministic generation with PRNG seed.
- Exact 16-bit binary heightmap serialization without external C++ or GUI dependencies.
- Mass conservation during erosion simulations.
- Zero regressions across existing test suite.
