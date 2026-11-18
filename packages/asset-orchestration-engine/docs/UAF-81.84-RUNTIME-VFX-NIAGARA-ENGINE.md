# UAF-81.84 — UNIVERSAL RUNTIME VFX, PARTICLE SIMULATION, EFFECT GRAPH & NIAGARA INTEGRATION SYSTEM

**Estado:** Fase normativa activa  
**Dependencias obligatorias:** UAF-81.73 Runtime World Model, UAF-81.74 Runtime Physics, UAF-81.75 Runtime Rendering, UAF-81.76 Runtime Audio, UAF-81.77 Runtime Input, UAF-81.79 Runtime Gameplay, UAF-81.80 Runtime Animation, UAF-81.81 Spatial Streaming/HLOD, UAF-81.82 Runtime AI, UAF-81.83 Runtime Networking, Event Bus determinista, Replay Engine, Checkpoint/Recovery, Asset Registry y sistema SHA-256 de estado canónico.

---

# 1. OBJETIVO GENERAL

UAF-81.84 implementa un **VFX Runtime Universal** desacoplado del motor gráfico y de Unreal Engine capaz de:

- Describir sistemas de efectos visuales mediante datos serializables e inmutables (`VFXSystem`, `VFXEmitter`, `ParticleSchema`).
- Ejecutar simulación de partículas CPU y simulación GPU abstracta (a través de compute shaders/buffers abstractos y un backend `REFERENCE` determinista como autoridad de certificación).
- Soportar emisores por tasa continua, ráfagas (`BURST`), distancia, eventos y sub-emisores recursivos.
- Implementar operadores matemáticos modulares, curvas con interpolación (lineal, constante, cúbica, bezier) y gradientes de color (RGB + Alpha).
- Aplicar campos de fuerzas físicas: gravedad, drag, viento, turbulencia (curl noise), vórtices, atractores, repulsores y colisiones contra geometrías planas, esféricas, cajas y SDFs de física de UAF-81.74.
- Renderizar partículas mediante sprites (billboard, velocity-aligned, flipbook Sub-UV), mallas 3D, ribbons/cintas, trails con historial temporal, rayos/beams y calcomanías (decals).
- Proveer niveles de detalle (`LOD0`..`LOD3`, `CULLED`), culling por frustum, distancia y oclusión, pooling de instancias sin estado fantasma (`ghost state`) y gestión estricta de presupuestos CPU/GPU con degradación ordenada.
- Integración nativa con eventos de gameplay, impactos físicos, disparadores de audio y celulado de streaming espacial (UAF-81.81).
- Replicación en red causal (replicar causas y eventos, no partículas individuales), con soporte de predicción en cliente y descarte de duplicados mediante ventana de `event_id`.
- Compilador y puente bidireccional con **Unreal Engine 5 Niagara** a través de una Representación Intermedia (UAF VFX IR), soporte de assets de referencia (Golden Assets), detección de compatibilidad y live-reload.
- Telemetría, profiling exhaustivo por subsistema, validación semántica e inmunidad ante fallos (aislamiento seguro para que un fallo en VFX nunca derribe el mundo ni el simulation tick).
- Certificación Golden VFX ejecutando simulación masiva (10.000+ partículas, 1.000+ emisores, 100+ sistemas), determinismo absoluto y tolerancia GPU/CPU cuantificada.

---

# 2. ARQUITECTURA DE CAPAS Y FLUJO DE DATOS

```
                    UAF VFX AUTHORING
                           │
                           ▼
                    VFX DESCRIPTION
                           │
                           ▼
                 UNIVERSAL VFX RUNTIME
                    │              │
                    ▼              ▼
              CPU SIMULATION    GPU BACKEND
                    │              │
                    └──────┬───────┘
                           ▼
                    PRESENTATION
                    │            │
                    ▼            ▼
                  UAF Renderer   UE5 Niagara Bridge
```

### Separación Simulación vs Presentación:
1. `DETERMINISTIC`: Partículas o efectos con impacto causal en gameplay/física/IA. Forman parte del `state_hash` canónico SHA-256.
2. `PRESENTATION_DETERMINISTIC`: Efectos visuales reproducibles deterministamente con la misma semilla RNG (`effect_seed`), pero excluidos del hash autoritativo de gameplay.
3. `NON_DETERMINISTIC_VISUAL`: Efectos cosméticos asíncronos o específicos de plataforma (e.g. partículas GPU ambientales).

---

# 3. SUB-FASES NORMATIVAS (81.84.0 - 81.84.12)

- **81.84.0**: Core Contracts, Data Model, Identidades, Schemas de Partícula.
- **81.84.1**: Emisores, Ciclo de Vida de Partículas, Modos de Spawn, Políticas de Capacidad y Desbordamiento.
- **81.84.2**: Curvas (Linear, Cubic, Bezier), Gradientes de Color y Operadores Matemáticos.
- **81.84.3**: Campos de Fuerza (Gravedad, Drag, Viento, Curl Noise, Turbulencia), Colisiones y Restricciones.
- **81.84.4**: Grafo de Efectos (DAG), Sistema de Eventos y Sub-Emisores en Cascada.
- **81.84.5**: Renderers de Partículas (Sprites, Meshes, Ribbons, Trails, Beams, Decals, Material Bindings).
- **81.84.6**: Backends de Simulación (`REFERENCE`, `CPU`, `GPU`).
- **81.84.7**: LOD, Culling, Object Pooling (Reset Limpio) y Budget Manager con Degradación.
- **81.84.8**: Integración con Gameplay, Física, Audio y Políticas de Streaming Espacial.
- **81.84.9**: VFX de Red, Replicación Causal, Predicción Local y Descarte de Duplicados.
- **81.84.10**: Niagara Bridge, Compilador UAF IR → Niagara, Export/Import, Compatibilidad y Live Reload.
- **81.84.11**: Profiling, Telemetría, Validación Semántica y Recuperación de Fallos (Fail-Safe Isolation).
- **81.84.12**: Certificación Golden VFX, Escenario Golden, Pruebas de Estrés y Verificación de Invariantes.
