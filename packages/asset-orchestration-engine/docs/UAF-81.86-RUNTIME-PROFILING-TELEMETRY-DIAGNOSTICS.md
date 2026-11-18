# UAF-81.86 — UNIVERSAL RUNTIME PROFILING, TELEMETRY, FRAME BUDGETING, DIAGNOSTICS & CRASH RECOVERY

**Estado:** Fase Normativa Activa  
**Dependencias:** UAF-81.73–81.85  
**Integración:** AOE, UAF Runtime, World Streaming, AI, Networking, Physics, Rendering, Animation, VFX, Lighting, Audio, UI, Persistence y UE5 Bridge.

---

# 1. MISIÓN Y PRINCIPIO FUNDAMENTAL

UAF-81.86 implementa el sistema universal de observabilidad, diagnóstico, presupuestación y recuperación del AOE/UAF, constituyendo el **sistema nervioso central** del motor.

El subsistema responde automáticamente:
- ¿Qué está ocurriendo y en qué fotograma/tick comenzó?
- ¿Dónde y por qué ocurrió? (Subsistema, hilo, recurso y llamada causal).
- ¿Qué recurso provocó la sobrecarga o fuga?
- ¿Se superó algún presupuesto (Soft, Warning, Hard, Emergency)?
- ¿Es una regresión estadística frente a la baseline histórica (P95/P99)?
- ¿Puede recuperarse automáticamente mediante degradación o checkpoints?
- ¿Permite reproducir de forma idéntica la divergencia de determinismo?

**Principio Fundamental:** Todo subsistema puede observarse sin modificar su lógica funcional y la telemetría nunca altera el estado autoritativo de gameplay.

---

# 2. REQUISITOS NO NEGOCIABLES

1. **No-Intrusión**: El profiler no altera el resultado de la simulación.
2. **Desacoplamiento**: Cero dependencias cruzadas introducidas por la telemetría.
3. **Unidades Explícitas**: Toda métrica declara su unidad (`milliseconds`, `microseconds`, `bytes`, `entities`, `draw_calls`, etc.).
4. **Marcas Temporales**: Todo evento posee timestamp y `frame_index` / `simulation_tick`.
5. **Memoria Acotada**: Búferes anulares (ring buffers) lock-free con desbordamiento controlado (`DROP_OLDEST`).
6. **Inmunidad ante Fallos**: Un fallo en telemetría o profiling jamás derriba la ejecución de gameplay.
7. **Búsqueda de Divergencia Determinista**: Detección binaria del primer frame y propiedad donde dos ejecuciones difieren en `state_hash`.
8. **Recuperación Escalonada**: 6 niveles de recuperación (`LEVEL 0` a `LEVEL 5`), culminando en `SAFE_MODE`.
9. **Calidad de CI y Gate Autónomo**: Evaluación automática `PASS` / `FAIL` / `RETRY` / `DEGRADE` / `ROLLBACK` / `QUARANTINE` / `CERTIFY`.

---

# 3. SUBFASES NORMATIVAS (81.86.0 — 81.86.21)

- **81.86.0**: Telemetry Core & Metric Data Model (Counters, Gauges, Histograms, Spans, Ring Buffers).
- **81.86.1**: Frame Budget Manager & Dynamic Negotiation (60/120/144 FPS targets, 11 subsystem allocations).
- **81.86.2**: Memory Profiler & Leak Detection (Ownership tracking, snapshot diffs, leak detector).
- **81.86.3**: Streaming Profiler (Cell IO, decompression, CPU generation, GPU upload, thrashing).
- **81.86.4**: Physics Profiler (Broadphase, narrowphase, solver, contacts, explosion detection).
- **81.86.5**: AI Profiler (Agents, BTs, NavMesh, RVO/ORCA, pathfinding storm detection).
- **81.86.6**: Network Profiler (Packets, bytes, RPCs, replication cost, jitter, prediction corrections).
- **81.86.7**: Animation Profiler (Skeleton updates, blend trees, IK, bone counts, hotspot character tracking).
- **81.86.8**: VFX Profiler (Emitters, CPU/GPU particles, simulation cost, overdraw, emitter leaks).
- **81.86.9**: Lighting Profiler (Dynamic lights, shadow maps, shadow atlas occupancy, volumetrics).
- **81.86.10**: Render & Overdraw Profiler (Draw calls, triangles, pipeline state changes, occlusion culling).
- **81.86.11**: Audio Profiler (Voices, mix cost, DSP effects, streaming, occlusion).
- **81.86.12**: UI Profiler (Widget count, layout passes, paint passes, layout thrashing).
- **81.86.13**: Diagnostic Event System & Correlation (Severity levels, contextual state hash correlation).
- **81.86.14**: Regression Engine & Benchmark Baselines (Mean, Median, P95, P99 statistical gates).
- **81.86.15**: Determinism Diagnostics & Divergence Search (Binary search pinpointing divergence frame/entity).
- **81.86.16**: Trace Recording & Ring Buffer (Formato `UAFTRACE`, persistencia inmediata ante anomalía).
- **81.86.17**: Crash Handling, Watchdogs & 6-Level Recovery (Watchdog timers, deadlock graphs, safe mode).
- **81.86.18**: Telemetry Storage, Session Manifests & AOE Integration (JSON/JSONL/binary, session audits).
- **81.86.19**: Remote Telemetry, Privacy & Security (Sanitización, cifrado, separación de datos de usuario).
- **81.86.20**: Dashboard Data Model & Inspectors (Frame Inspector, Resource Inspector, Budget Dashboard).
- **81.86.21**: Testing, Stress Test (10.000 entidades) & Golden Performance Certification.
