# UAF-81.94: PROCEDURAL INTERACTIVE AUDIO, SPATIAL ACOUSTICS & METASOUNDS (UE5 AUDIO FABRIC)

**Status:** Approved & Normative  
**Subsystem:** Universal Asset Framework (AOE/UAF) - Interactive Sound & MetaSounds Integration  
**Target Engine:** Unreal Engine 5 (MetaSounds Source Assets, SoundAttenuation, Quartz Subsystem, Audio Gameplay Effects)  
**Execution Environment:** 100% Headless Orchestrator & Exporter  

---

## 1. MISSION & SCOPE

UAF-81.94 establishes an analytical, physical, and adaptive audio engine within the Universal Asset Framework. Building upon WFC level topologies and pacing stress curves (UAF-81.90), macroscopic landscapes (UAF-81.91), multi-agent NPC squads (UAF-81.92), and weapon itemization (UAF-81.93), UAF-81.94 solves interactive acoustic immersion.

The subsystem operates entirely headlessly with zero external engine dependencies, synthesizing:
1. **Adaptive Multi-Stem Orchestration**: Seamless equal-power crossfading across musical stems synchronized to bar boundaries via a simulated **Quartz** quantization clock.
2. **Sabine & Eyring Physical Acoustics**: Analytical calculation of frequency-dependent reverberation decay ($RT_{60}$) and axial standing wave resonance modes across modular rooms.
3. **Topological Acoustic Diffraction**: Sound transmission loss and low-pass filtering through corners, portals, and closed security doors.
4. **3D Spatial Attenuation & Rule 10 Enforcement**: Positional distance roll-off, atmospheric air absorption, and strict clamping of continuous enemy SFX to closed falloff radii ($\le 20.0\text{ m}$).
5. **MetaSounds Graph Exporter**: Structured JSON manifests for **MetaSounds Source Assets** and native `USoundAttenuation` presets.

---

## 2. MATHEMATICAL & ARCHITECTURAL SPECIFICATIONS

### 2.1 Adaptive Stems & Equal-Power Crossfade
Musical layers are organized into specialized roles (`ATMOSPHERE_PAD`, `BASS_SYNTH`, `DRUMS_PERCUSSION`, `MELODIC_LEAD`, `TENSION_NOISE`, `COMBAT_RISER`). Transitioning between `DynamicPacingDirector` phases (`CALM`, `BUILDUP`, `PEAK`, `SUSTAINED_PEAK`, `COOLDOWN`) executes on exact musical bar boundaries:

$$t_{\text{boundary}} = \left(\left\lfloor \frac{t_{\text{current}}}{\Delta t_{\text{grid}}} \right\rfloor + 1\right) \cdot \Delta t_{\text{grid}}$$

Crossfading between incoming stem $g_{\text{in}}$ and outgoing stem $g_{\text{out}}$ over normalized progress $t \in [0.0, 1.0]$ uses the constant-power trigonometric law:

$$g_{\text{in}}(t) = \sin\left(\frac{\pi}{2} \cdot t\right), \quad g_{\text{out}}(t) = \cos\left(\frac{\pi}{2} \cdot t\right)$$

This strictly preserves perceived loudness and root-mean-square (RMS) invariant energy across all transitions:
$$g_{\text{in}}^2(t) + g_{\text{out}}^2(t) = \sin^2\left(\frac{\pi}{2} t\right) + \cos^2\left(\frac{\pi}{2} t\right) = 1.0$$

### 2.2 Physical Reverberation: Sabine & Eyring Formulations
For an enclosed room of volume $V = L \cdot W \cdot H$ and total surface area $S = 2(LW + LH + WH)$, with material area fractions $f_i$ having absorption coefficients $\alpha_i$, the mean absorption is:

$$\bar{\alpha} = \sum_{i} f_i \cdot \alpha_i, \quad A = S \cdot \bar{\alpha}$$

- **Sabine Reverberation Time**:
  $$RT_{60}^{\text{Sabine}} = \frac{0.161 \cdot V}{A} = \frac{0.161 \cdot V}{S \cdot \bar{\alpha}}$$
- **Eyring Reverberation Time** (accurate for absorbent and damped spaces):
  $$RT_{60}^{\text{Eyring}} = \frac{0.161 \cdot V}{-S \ln(1 - \bar{\alpha})}$$

**Axial Room Resonance Modes**:
Harmonic standing wave frequencies along Cartesian axes for integer mode numbers $(n_x, n_y, n_z)$ with speed of sound $c = 343.0\text{ m/s}$:

$$f_{n_x, n_y, n_z} = \frac{c}{2} \sqrt{\left(\frac{n_x}{L}\right)^2 + \left(\frac{n_y}{W}\right)^2 + \left(\frac{n_z}{H}\right)^2}$$

### 2.3 Topological Sound Diffraction & Door Isolation
Sound traversing a level topology experiences barrier transmission loss and frequency filtering:
- `CLEAR_LOS`: Same room, direct transmission loss $0\text{ dB}$, low-pass cutoff $20000\text{ Hz}$.
- `PORTAL_DIFFRACTION`: Open adjacent room, transmission loss $+6.0\text{ dB}$, low-pass cutoff $5000\text{ Hz}$.
- `FULL_OCCLUDED` (Closed Security Door): Transmission loss $+24.0\text{ dB}$ per door, low-pass cutoff clamped to $800.0\text{ Hz}$ (deep muffle).

### 2.4 3D Positional Spatialization & Rule 10 Enforcement
In accordance with Rule 10 of `AGENTS.md`:
1. Every ambient entity, enemy engine hum, or patrol state loop **must possess positional 3D attenuation with falloff $\le 20.0\text{ m}$**.
2. Beyond $r_{\text{falloff}}$, linear gain is strictly $0.00$ ($-\infty\text{ dB}$), eliminating background noise accumulation.
3. Natural Exponential Distance Roll-Off:
   $$g(d) = \begin{cases} 
   1.0 & d \le r_{\text{inner}} \\ 
   \left(1.0 - \frac{d - r_{\text{inner}}}{r_{\text{falloff}} - r_{\text{inner}}}\right)^2 & r_{\text{inner}} < d < r_{\text{falloff}} \\ 
   0.0 & d \ge r_{\text{falloff}} 
   \end{cases}$$
4. Atmospheric Air Absorption:
   $$f_{\text{cutoff}}(d) = 20000 \cdot 10^{-\frac{d \cdot \beta_{\text{air}}}{20}}$$
   where $\beta_{\text{air}} = 0.5\text{ dB/m}$.

### 2.5 Unreal Engine 5 MetaSounds Graph Schema
Exports generate:
- Structured JSON graph specification for `MS_AdaptiveMusicDirector` exposing dynamic input pins (`Trigger.Play`, `Param.PacingStress`, `Param.RoomRT60`, `Param.OcclusionLowPassCutoff`).
- Native `USoundAttenuation` asset definitions configured with binaural spatialization and air absorption LPF.
- Editor Python script `aoe_metasounds_ingest.py` for automated Unreal Editor asset creation.

---

## 3. ACCEPTANCE CRITERIA
- 100% mathematical accuracy of Sabine and Eyring $RT_{60}$ equations.
- Verification of constant-power crossfades ($g_{\text{in}}^2 + g_{\text{out}}^2 \approx 1.0$).
- Quartz quantization clock scheduling exact timestamps to musical bar boundaries.
- Topological acoustic transmission loss correctly evaluating closed doors (+24 dB).
- Strict Rule 10 compliance: zero sound outside falloff and looping falloff bounded at $\le 20.0\text{ m}$.
- Complete MetaSounds Source Asset and SoundAttenuation JSON manifests.
- Zero regressions across the global test suite (> 8,702 tests passing at 100%).
