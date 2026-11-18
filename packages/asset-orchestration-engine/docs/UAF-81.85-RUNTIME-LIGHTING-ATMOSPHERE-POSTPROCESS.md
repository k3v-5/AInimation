# UAF-81.85 — UNIVERSAL DYNAMIC LIGHTING, SHADOWS, ATMOSPHERE & POST-PROCESS SYSTEM

**Estado:** Fase Normativa en Ejecución  
**Dependencias:** UAF-81.73 Runtime World, UAF-81.74 Runtime Physics, UAF-81.75 Runtime Rendering, UAF-81.80 Runtime Animation, UAF-81.81 World Streaming, UAF-81.82 Runtime AI, UAF-81.83 Runtime Networking, UAF-81.84 Universal VFX Runtime.

---

# 1. OBJETIVO GENERAL

UAF-81.85 implementa la arquitectura universal de iluminación dinámica, sombras, atmósfera y postprocesado del Asset Orchestration Engine (AOE). Funciona de forma 100% headless, determinista y desacoplada de hardware de GPU o de Unreal Engine, permitiendo su ejecución en pipelines de pruebas, certificación e interoperabilidad con Unreal Engine 5.

El subsistema proporciona:
- Iluminación física fotométrica estática y dinámica (Point, Spot, Directional, Rect, Disk, Line, Emissive, Environment).
- Conversión determinista de temperatura de color Kelvin (1000K → 20000K+) a RGB lineal.
- Sistema universal de sombras con soporte de CSM (Cascaded Shadow Maps), Shadow Atlas, Contact Shadows, bias numérico y LOD de sombras.
- Iluminación global/ambiental mediante Probes (Irradiance, Reflection, Light Probe Grid) y modo de baking precomputado.
- Sistema de cielo, Sol, Luna y ciclo Día/Noche con efemérides astronómicas desacopladas de tiempo de reloj de pared.
- Atmósfera física con dispersión de Rayleigh (\(\lambda^{-4}\)), Mie (Henyey-Greenstein), capa de ozono y niebla volumétrica con decaimiento exponencial por altura.
- Capa de nubes volumétricas e integración de condiciones meteorológicas propagadas hacia iluminación y VFX.
- Pipeline HDR, control de exposición (manual, automática con adaptación temporal), tone mapping (ACES, Filmic, AgX, Neutral) y gestión de color/LUTs.
- Stack de postprocesado para cámaras con volúmenes de prioridad acotados y globales no acotados (Bloom, AO, Motion Blur, DOF, efectos de lente).
- LOD de iluminación, culling multinivel (frustum, distancia, influencia de pantalla) y escalera de degradación de presupuestos en 7 niveles.
- Integración simétrica con World Streaming (UAF-81.81), PBR Materials, VFX (UAF-81.84), Cámara y Replicación en Red (UAF-81.83).
- Puente de exportación y sincronización en vivo hacia Unreal Engine 5 (Lumen, SkyAtmosphere, VolumetricCloud, ExponentialHeightFog, PostProcessSettings).
- Profiling frame a frame, validación semántica estricta (rechazo de NaN/Inf y valores no físicos) y aislamiento seguro ante fallos con 4 niveles de fallback (`FULL`, `REDUCED`, `MINIMAL`, `EMERGENCY`).
- Certificación Golden Lighting con 14 escenarios de referencia y prueba de estrés masiva (10.000 luces dinámicas, 1.000 casters de sombra).

---

# 2. ARQUITECTURA Y FLUJO DE DATOS

```text
                    LIGHTING AUTHORING
                           │
                           ▼
                 LIGHTING DESCRIPTION
                           │
                           ▼
                 LIGHTING IR / GRAPH
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
       UAF LIGHTING RUNTIME        UE5 ADAPTER
              │                         │
       ┌──────┼───────┐                 ▼
       ▼      ▼       ▼              UE5
     CPU     GPU   REFERENCE
       │      │
       └──────┴───────┐
                      ▼
              POST PROCESS
                      │
                      ▼
                  FRAME OUTPUT
```

### Separación Estricta de Estados
1. **Gameplay State** (Autoritativo): Física, IA, Reglas de Juego, Transformaciones de Entidades.
2. **Presentation State** (No Autoritativo en Juego): Iluminación, Sombras, Volumetría, Post-Process. Ningún cálculo de iluminación puede alterar variables críticas de gameplay (salud, colisión, victoria).

---

# 3. DESCOMPOSICIÓN EN SUBFASES NORMATIVAS

- **81.85.0 — Lighting Core & Illumination Data Model**: Contratos base, identidades inmutables (`LightId`, `ShadowCasterId`, `VolumeId`, `ProbeId`), esquemas con versión y revisión, conversión Kelvin a RGB lineal, validación finita.
- **81.85.1 — Dynamic Light Types & Light Management**: Entidades de luz, atenuación cuadrática inversa con radio de corte suave, conos de foco, movilidad (`STATIC`, `STATIONARY`, `MOVABLE`), prioridades (`CRITICAL`, `GAMEPLAY`, `CHARACTER`, `ENVIRONMENT`, `VFX`, `COSMETIC`), attachments jerárquicos.
- **81.85.2 — Shadow System**: Interfaz `ShadowProvider`, backends (`ShadowMap`, `CSM`, `CubeShadow`, `AtlasShadow`, `VirtualShadow`, `RayTracedShadow`, `ReferenceShadow`), división de cascadas CSM con estabilización de texels, atlas de sombras, sesgos (constant, slope, normal), contact shadows y shadow LOD.
- **81.85.3 — Global / Ambient Illumination**: Iluminación ambiental base, sondas de irradiancia y reflexión, rejilla tridimensional `LightProbeGrid`, soporte de baking y particionado espacial compatible con streaming.
- **81.85.4 — Sky, Sun, Moon & Day/Night Cycle**: Controlador de tiempo desacoplado (`simulation_time`, `world_time`, `calendar_time`), cálculo determinista de efemérides (acimut, elevación solar/lunar según latitud, longitud y fecha), fase y diámetro angular lunar, transiciones armónicas.
- **81.85.5 — Atmosphere, Fog & Volumetric Lighting**: Modelo físico de dispersión atmosférica (Rayleigh, Mie, Ozono, Aerosol), niebla exponencial con atenuación por altura, raymarching volumétrico de luz con función de fase de Henyey-Greenstein y LOD volumétrico.
- **81.85.6 — Clouds & Weather Lighting Integration**: Cobertura, altitud, densidad y deriva de nubes por vector de viento; presets meteorológicos (`clear`, `cloudy`, `overcast`, `storm`, `fog`, `rain`, `snow`, `dust`, `sandstorm`) y acoplamiento de eventos meteorológicos con el bus de eventos de UAF-81.84.
- **81.85.7 — Exposure, HDR, Tone Mapping & Color Management**: Pipeline lineal HDR, auto-exposición por histograma y luminancia media con adaptación temporal, backends de mapeo tonal (`ACES`, `Filmic`, `AgX`, `Neutral`), gradación de color (temperatura, tinte, contraste, ganancia, gamma, elevación), LUT 1D y 3D.
- **81.85.8 — Post-Process Stack**: Evaluación y mezcla ponderada por prioridad de `PostProcessVolume` (volúmenes globales infinitos vs volúmenes locales con radio de mezcla), Bloom anamórfico piramidal, Ambient Occlusion (`SSAO`, `GTAO`), Motion Blur, Depth of Field (círculo de confusión) y efectos de lente (viñeta, aberración cromática, grano).
- **81.85.9 — Lighting LOD, Culling, Baking & Budgets**: Culling espacial por frustum, distancia, influencia de pantalla y oclusión; frecuencias de refresco (`EVERY_FRAME`, `EVERY_2_FRAMES`, `EVERY_4_FRAMES`, `EVENT_DRIVEN`, `STATIC`); degradación presupuestaria en 7 pasos bajo sobrecarga de recursos.
- **81.85.10 — Materials, VFX, World & Camera Integration**: Interacción PBR (emisión, subsuperficie, rugosidad), spawn de luces desde emisores VFX de UAF-81.84, autoridad de cámara, carga y descarga simétrica vinculada a celdas de World Streaming (UAF-81.81) sin fugas ni recursos huérfanos.
- **81.85.11 — UE5 Lighting/Niagara/Post-Process Bridge**: Mapeo y generación de manifiestos para componentes de Unreal Engine 5 (`UDirectionalLightComponent`, `USkyAtmosphereComponent`, `UVolumetricCloudComponent`, `UExponentialHeightFogComponent`, `FPostProcessSettings`), auditoría de compatibilidad (features soportadas, no soportadas, lossy) y soporte de actualización en vivo.
- **81.85.12 — Profiling, Validation & Recovery**: Métricas de rendimiento por fotograma (tiempos CPU/GPU, conteos, memoria), validación semántica completa contra corrupción numérica, aislamiento contra excepciones y degradación automática a 4 perfiles de fallback (`FULL`, `REDUCED`, `MINIMAL`, `EMERGENCY`).
- **81.85.13 — Golden Lighting Certification**: Mundo de certificación Golden Lighting, 14 escenarios de referencia, prueba de estrés de 10.000 luces dinámicas y 1.000 casters de sombra, serialización determinista de snapshots y comprobación del hash canónico SHA-256.
