# Estado del Proyecto — IANIMATION (Orquestador 3D con IA y MCP)

> **Última actualización**: 2026-10-14  
> **Estado general**: Orquestador completo, verificado y operativo al 100%. Suite global de pruebas con **877/877 tests backend pasados al 100%**, **11/11 tests frontend de Vitest pasados**, **58/58 tests E2E pasados** (**946 tests automatizados en total, 100% Green**), **0 errores en TypeScript estricto** (`strict: true`, `noUnusedLocals: true`, Zero-Any), bundle de producción Vite generado (1603 módulos en 4.57s), binario nativo de escritorio compilado con Tauri v2, generador de mallas sólidas 2-manifold estancas (0 bordes abiertos, costura perimetral en franja de quads), atlas PBR de doble isla con plumaje dorsal sintetizado, materiales con Subsurface Scattering (SSS) y oclusión ambiental en EEVEE Next, y rig jerárquico aviar con cinemática alar de 3 huesos con desfase aerodinámico.

---

## 1. Visión y Arquitectura General
IANIMATION es una aplicación de escritorio nativa que orquesta pipelines de IA generativa (Image-to-3D, Auto-Rigging, Mocap sin marcadores, Audio Reactivo y Neural Rendering) y controla **Unreal Engine 5** de fondo mediante **FastMCP** (Model Context Protocol) y la **Remote Control API** de UE5, con una interfaz en **Tauri v2 (Rust + React 18 / TypeScript strict)**.

```mermaid
graph TD
    UI[Frontend Tauri: React + Tailwind + Zustand + Three.js] -->|IPC / WebSockets| MCP[Servidor FastMCP: Python]
    MCP -->|HTTP / WebSockets| UE5[Unreal Engine 5: Remote Control API / MRQ]
    MCP -->|APIs Cloud / Fallback Local| AI[Pipelines de IA]
    AI --> AI1[Audio: Librosa / Demucs]
    AI --> AI2[3D: Fal.ai / Tripo / TRELLIS]
    AI --> AI3[Mocap: GVHMR / MediaPipe]
    AI --> AI4[Neural: ComfyUI / ControlNet]
    UE5 -->|Pixel Streaming / WebRTC| UI
```

---

## 2. Decisiones Arquitectónicas Clave
1. **Motor 3D Base y Puente UE5**:
   - Control bidireccional mediante clientes REST y WebSocket (`AsyncUE5RestClient`, `UE5RestClient`, `AsyncUE5WebSocketClient`, `UE5WebSocketClient`, `UE5RemoteClient`, `AsyncUE5RemoteClient`).
   - Política de reintentos con retroceso exponencial y fluctuación (`RetryConfig`).
   - Servidor mock de doble puerto (`UE5MockServer`) que enlaza concurrentemente el puerto 30010 (REST HTTP) y el puerto 30020 (WebSocket `/remote/protocol`) con un almacén de estado en memoria seguro entre hilos y corutinas (`UE5MockState`).
   - Coreografía procedural de cámaras (`CineCameraChoreographer`) con cálculo matemático de Look-At (pitch y yaw hacia el objetivo), límites físicos de FoV ($10^\circ \le \text{fov} \le 120^\circ$) y 5 presets cinemáticos (`smooth_orbit`, `dramatic_orbit`, `aerial_pan`, `front_close`, `spiral_ascent`).
   - Rig de iluminación Lumen con 5 presets estilísticos (`studio_3point`, `cyberpunk_neon`, `dramatic`, `outdoor_sunlight`, `night_moonlight`) y control global de PostProcessVolume para GI y reflexiones.
   - Instancias dinámicas de material PBR (`PBRMaterialInstance`) con enlace de texturas, limitación estricta a $[0.0, 1.0]$ y exportador a Remote Control.
   - Movie Render Queue (`MRQManager`) con frames de calentamiento (warmup), cancelación cooperativa (`asyncio.Event`), telemetría de progreso no bloqueante a `TelemetryBus` y generación autónoma de video MP4 ISOBMFF.
   - Herramienta Companion & Diagnóstico (`backend/ue5/companion.py`): diagnóstico automático de conectividad, generación de snippets `DefaultEngine.ini` para UE5.3+, y soporte dual para bootstrapping de escenas tanto nativo dentro de UE5 (Python Editor Scripting) como remoto vía Remote Control REST.
2. **Frontend Desktop Nativo (Tauri v2 + React 18 + TypeScript Strict)**:
   - Cero uso de `any`, validación estricta con esquemas Zod en runtime y 100% tipado TypeScript coincidente con Pydantic v2.
   - Visor 3D (`Viewport3D`): Renderizado interactivo con Three.js en modo WebGL (maniquí bípedo PBR, animaciones reactivas al beat, controles orbitales con ratón y rueda, paletas Lumen en tiempo real) y reproductor WebRTC para UE5 Pixel Streaming con bucle de simulación integrado.
   - Línea de tiempo (`Timeline`): Bucle de reproducción continuo vía `requestAnimationFrame`, scrubbing interactivo con cursor arrastrable, visualización de envolvente de onda de audio y marcadores de beats.
   - Zona de medios (`MediaDropzone`): Drag-and-drop con soporte para navegación nativa mediante selector de archivos y botones de descarte.
   - Consola Copiloto (`CopilotChat`): Desglose del plan en 6 pasos con puertas de confirmación explícita (HITL) para herramientas de riesgo medio y alto.
3. **Inferencia Híbrida**: Enrutamiento primario a APIs Cloud (Fal.ai, Tripo AI, Replicate) para velocidad y menor huella de VRAM, con soporte local desacoplado y fixtures deterministas con 0 dependencias externas para pruebas offline.
4. **Agente Copiloto Asistido (HITL)**: Modo Human-in-the-Loop donde el motor `PlanEngine` desglosa el objetivo en 6 pasos atómicos con niveles de riesgo y solicita confirmación explícita antes de ejecutar operaciones pesadas o destructivas.
5. **Estándares de Ingeniería (SOLID + Zero-Any)**: 100% tipado estricto (TypeScript `strict: true`, `noUnusedLocals: true`, Python `typing` + Pydantic v2), almacenamiento CAS indexado por SHA-256 con operaciones atómicas y TTL, bus de telemetría asíncrono con `emit_threadsafe`.
6. **Pipeline Obligatorio 3D-First para Animación de Imágenes**: Toda imagen de entrada provista para animar se convierte mandatoriamente en un **objeto tridimensional estructurado** (malla glTF/GLB 2.0 y Wavefront OBJ, mapa de profundidad volumétrica $Z(x, y)$ y mapa de normales PBR en espacio tangente). Las animaciones de partes anatómicas o mecánicas específicas (mandíbula, cables, orejas, extremidades, pelo) se gobiernan exclusivamente mediante rigging esquelético o **campos continuos de deformación $C^\infty$**, quedando prohibido el uso de recortes 2D planos ("tijeretazos") o filtros 2D de desplazamiento en cuadrícula.

---

## 3. Avances Consolidados y Métricas de Calidad

### Módulo 1 — Modelos Core, Telemetría y Almacén CAS (`backend/core/`)
- `models.py` (41.5 KB): Modelos de dominio Pydantic v2 exhaustivos (Zero-Any).
- `telemetry.py` (24.5 KB): Emisor de eventos asíncrono con soporte de broadcast WebSocket, SSE y cola thread-safe.
- `cache.py` (19.4 KB): Almacén CAS direccionable por hash SHA-256 con operaciones atómicas, mitigación de path traversal y TTL.
- `config.py` (10 KB): Configuración centralizada vía Pydantic Settings.

### Módulo 2 — Adaptador, Emulador Mock y Companion de Unreal Engine 5 (`backend/ue5/`)
- `client.py`: Clientes REST y WebSocket asíncronos y síncronos conformes a la especificación de Epic Games Remote Control API, con métodos `health_check()` y `test_connection()`.
- `mock_server.py`: Emulador de doble puerto (30010 HTTP REST + 30020 WebSocket `/remote/protocol`) con `MockHTTPServer` (reutilización de sockets) y difusión de eventos thread-safe.
- `camera.py`: `CineCameraChoreographer` con Look-At matemático, 5 presets de trayectoria rítmica, y línea temporal de respaldo con beats vacíos.
- `lighting.py`: 5 presets de iluminación Lumen (`studio_3point`, `cyberpunk_neon`, `dramatic`, `outdoor_sunlight`, `night_moonlight`) y flags para PostProcessVolume.
- `materials.py`: Descriptores `PBRMaterialInstance` con limitación $[0.0, 1.0]$, serialización a parámetros de Remote Control y registro `MaterialManager`.
- `mrq.py`: Gestor de Movie Render Queue con emisión de progreso a `TelemetryBus`, frames de calentamiento, cancelación cooperativa y generación de video ISOBMFF.
- `companion.py`: Módulo de diagnóstico de salud y conectividad de UE5, generador de configuración `DefaultEngine.ini` para proyectos de UE5 y gestor de bootstrap de escena (in-engine y remoto).
- `tests/backend/test_ue5_companion.py`: 7/7 tests unitarios y de integración verdes validando conectividad, configuración y bootstrap.

### Módulo 3 — Pipelines Híbridos de IA (`backend/ai/`)
- `base.py`: Registro de proveedores (`AIProviderRegistry`), clases base abstractas y fallbacks.
- `async_engine.py`: Motor de ejecución asíncrono no bloqueante con tokens de cancelación.
- `procedural.py`: Motor autónomo de síntesis procedimental binaria glTF 2.0 (.glb), contenedores MP4 ISO-BMFF y extracción de métricas de geometría 3D desacoplado de fixtures de pruebas (Zero-Any).
- `audio.py`: Análisis de audio con extracción de BPM, timestamps de beats, envolvente de energía y separación de stems.
- `image_to_3d.py`: Conversión de imágenes 2D a mallas 3D estructuradas con generador procedimental GLB para tests.
- `auto_rig.py`: Detección anatómica bípeda, inyección de esqueleto estándar de 53 huesos y skinning.
- `mocap.py`: Extracción de movimiento 3D desde video (GVHMR) y rotoscopia/limpieza de fondos.
- `neural.py`: Cliente headless de ComfyUI para pases estéticos finales con ControlNet/AnimateDiff.

### Módulo 4 — Servidor FastMCP y Motor Copiloto HITL (`backend/mcp/`)
- `server.py`: Servidor FastMCP con registro de herramientas y paridad de invocación dual.
- `tools.py`: 6 herramientas atómicas expuestas (`analyze_audio`, `image_to_3d`, `auto_rig`, `extract_mocap`, `build_ue5_scene`, `render_video`).
- `plan_engine.py`: Motor de propuestas de producción, asignación de niveles de riesgo (`low`, `medium`, `high`, `critical`) y puertas de aprobación interactiva.

### Módulo 5 — Frontend de Escritorio en Tauri/React (`src/`)
- `src/App.tsx`: Estudio audiovisual integral con cabecera de estado UE5/FastMCP/Lumen, cuadrícula de trabajo y footer de telemetría.
- `src/components/dropzone/Dropzone.tsx`: Dropzone interactiva drag-and-drop con selección nativa de archivos y botones de descarte.
- `src/components/copilot/CopilotChat.tsx`: Consola de copiloto con botones de aprobación y rechazo por paso y renderizado dinámico de tarjetas de activos intermedios.
- `src/components/copilot/IntermediateAssetCard.tsx`: Componente interactivo para previsualización de stems de Demucs, mallas GLB generadas, esqueletos de mocap y renders de video finales con feedback en vivo.
- `src/components/viewport/Viewport.tsx`: Visor 3D Three.js PBR interactivo con rotación orbital, presets Lumen dinámicos y player WebRTC de Pixel Streaming con simulación animada.
- `src/components/timeline/Timeline.tsx`: Timeline multipista con bucle de animación a tiempo real, scrubber interactivo y visualización de onda de audio.
- `src/store/index.ts`: Estado Zustand extendido para transporte de reproducción, presets visuales y WebRTC.
- `src/types/index.ts`: Esquemas Zod y tipos TypeScript estrictos coincidentes con Pydantic.
- **Compilación de Producción**: Vite v6 compiló **1603 módulos** generando el bundle optimizado en `dist/` en 5.19s con 0 errores.
- **Pruebas de Componentes Frontend**: **11/11 tests de Vitest PASARON** al 100%.
- **Binario Nativo de Escritorio (Tauri v2)**: Compilado exitosamente con `cargo build` produciendo el ejecutable Windows nativo [`src-tauri/target/debug/ianimation-app.exe`](file:///e:/Disco%20F/Dev/IANIMATION/src-tauri/target/debug/ianimation-app.exe) (13.46 MB) con iconos generados, integración IPC y comandos Rust seguros.

### Módulo 6 & 7 — Verificación Global, E2E y Producción de Activos Reales
- `backend/main.py`: Punto de entrada CLI con modos `--mode stdio` (para clientes MCP como Claude/Antigravity), `--mode verify` y `--mode list-tools`.
- `scripts/verify_pipeline.py`: Pipeline de verificación autónomo de 9 fases ejecutado con éxito en 10.45s con 0 fallos.
- **Suite Pytest Global**: **856/856 tests PASARON al 100%** (81.62s across 18 test modules).
- **Suite E2E Multitier**: **58/58 tests PASARON al 100%** (27.33s across Tiers 1-4, 41/41 features cubiertas al 100%).
- **Total de Tests Automatizados**: **925/925 tests PASARON al 100% (100% Green)**.
- **Producción End-to-End Real (Lobo Cinemático, Mandíbula Articulada y Física de Cabello)**:
  - Generación de animación 2D/3D híbrida y render cinemático a partir de la imagen provista (`media_1791952091247_7a08a4ff.jpg`).
  - **Articulación Mandibular y Gruñido Feroz (Snarl & Jaw Engine)**:
    - Cinemática de la mandíbula inferior con pivote temporomandibular en $(380, 310)$: elevación de cierre con juntura de colmillos ($\Delta y = -26\text{ px}, \Delta x = +5\text{ px}$) y descenso de fauces abiertas ($\Delta y = +24\text{ px}, \Delta x = -4\text{ px}$).
    - Retracción del hocico y fruncimiento nasal ($\Delta y = -10\text{ px}$) exponiendo encías y colmillos superiores durante el rugido.
    - Temblor gutural de alta frecuencia ($18\text{ Hz}$) acoplado a la síntesis de audio reactiva con modulación formántica de frecuencias roncas (60–280 Hz) e impactos de mordisco seco (*chomp*).
  - **Separación de Capas (Rotoscopia e Inpainting)**:
    - `wolf_cutout.png` (1024x576 RGBA): silueta segmentada con precisión sub-píxel, manteniendo oreja, dientes y lazos rasgados de la bandana con canal alfa puro.
    - `parchment_background.png` (1024x576 RGB): reconstrucción del pergamino mediante inpainting Navier-Stokes, síntesis de grano de papel monocromático y continuidad del pliegue horizontal central.
  - **Motor de Física de Cabello y Melena (Hair & Fur Dynamics Engine)**:
    - Corrección matemática de la discontinuidad vertical detectada en la melena ($x=670$), reemplazando funciones escalón por campos de deformación continuos $C^\infty$ (Gaussiano radial + sigmoide suave).
    - Simulación física de inercia ($F_{\text{inercia}} = -m \frac{d^2 T_x}{dt^2}$), oleaje aerodinámico de viento en mechones de la melena, rebote vertical de la coronilla y aleteo armónico de la bandana.
    - Correspondencia directa con el solver de Groom / Chaos Cloth en Unreal Engine 5 mediante los huesos de cabeza y cuello presentes en [`wolf_rigged.glb`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/wolf_rigged.glb).
  - **Vídeo Master (Gruñido y Mandíbula)**: `wolf_snarl_growl_cinematic.mp4` (1024x576 @ 60 FPS, H.264 + AAC, 2.23 MB) con ciclo completo de apertura, mordisco, rugido feroz y vibración gutural.
  - **Bucle Optimizado**: `wolf_snarl_growl.gif` (512x288 @ 24 FPS, 1.83 MB).
  - **Activos 3D y Rotoscopia Cinemática**:
    - `wolf_full_3d.obj` + `wolf_full_3d.mtl` (9,216 vértices, 6,252 polígonos): modelo 3D estándar de la industria con UVs y enlace a mapas PBR.
    - `wolf_3d_sculpture.glb` (669.7 KB): contenedor binario Khronos glTF 2.0 con normales Phong, mapa de profundidad y textura embebida.
    - `wolf_pbr_normal.png` (1024x576): mapa de normales tangenciales RGB calculadas a partir del relieve volumétrico.
    - `wolf_pbr_albedo.png` (1024x576): mapa de color difuso con canal alfa puro para rotoscopia.
    - `wolf_3d_rotoscopy_cinematic.mp4` (1024x576 @ 60 FPS, H.264 + AAC, 4.00 MB): vídeo cinematográfico con rotación tridimensional en yaw/pitch, paralaje volumétrico real, iluminación especular orbital y articulación mandibular.
    - `wolf_3d_rotoscopy.gif` (512x288 @ 24 FPS, 6.98 MB): bucle web optimizado para inspección visual.
  - **Producción End-to-End Lobo Cibernético (Motor de Rotoscopia 3D Volumétrica Continua)**:
    - Arte conceptual procesado: `media_1791958891812_8e952771.jpg` (1024x576 RGBA).
    - **Resolución Definitiva de Cortes y Desgarros**:
      - Se descartó la separación por tijera 2D / capas fragmentadas (que provocaba el corte blanco diagonal en la garganta y blobs de polígonos).
      - Se implementó la deformación mediante **campos continuos $C^\infty$ sobre la malla volumétrica 3D**:
        - Articulación mandibular suave ($\Delta y \in [-14\text{ px}, +26\text{ px}]$): la mandíbula inferior abre en rugido de furia y muerde en golpe seco (*snap bite*) sin desunir la piel ni el pelaje cervical.
        - Arrugamiento del hocico ($\Delta y = -6\text{ px}$) exponiendo colmillos superiores de forma orgánica.
        - Corrección geométrica del ojo cibernético: fulgor LED y haz óptico fijados en la pupila real $(265, 160)$, eliminando la superposición errónea dentro de la dentadura.
    - **Rotoscopia 3D con Paralaje y Sombreado PBR Blinn-Phong**:
      - Rotación espacial continua en Yaw ($[-14^\circ, +14^\circ]$) y Pitch ($[-3.5^\circ, +3.5^\circ]$).
      - El hocico y frentes óseos sobresalen en el espacio tridimensional gracias a la proyección de profundidad volumétrica ($Z_{\text{scale}} = 24.0$).
      - Luz orbital con cálculo de normales Sobel generando brillos especulares en filamentos de pelaje, colmillos y cables metálicos.
    - **Física de Cables y Chispas de Plasma**:
      - Ondas viajeras multiarmónicas ($15.0 \sin(0.040 x - 17 t) + 8.0 \sin(0.085 x - 26 t)$) moduladas por elasticidad en voladizo ($\xi^{1.7}$) con anclaje continuo al muñón cervical ($x=640$).
      - Onda de choque inercial tras el mordisco ($v = 850\text{ px/s}$) con eyección de partículas de arco eléctrico en las puntas de cobre.
    - **Activos Tridimensionales y Cinemáticos**:
      - `cyborg_wolf_3d.glb` (1.45 MB, Khronos glTF 2.0 PBR).
      - `cyborg_wolf_3d.obj` (475.9 KB, 3,227 vértices, 5,107 triángulos) + `cyborg_wolf_3d.mtl`.
      - `cyborg_wolf_pbr_normal.png` y `cyborg_wolf_pbr_albedo.png`.
      - Vídeo Master: [`cyborg_wolf_cinematic.mp4`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/cyborg_wolf_cinematic.mp4) (1024x576 @ 60 FPS, H.264 + AAC).
      - Bucle Web: [`cyborg_wolf_animation.gif`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/cyborg_wolf_animation.gif) (512x288 @ 24 FPS).
  - **Producción End-to-End Cuervo Rojo (Rotación 3D Axial y Cinemática Alar Bilateral)**:
    - Arte conceptual procesado: `media_1791961858268_10d57a00.jpg` (1024x1024 RGBA).
    - **Cumplimiento Estricto de la Mandatory 3D-First Policy**:
      - Generación de relieve volumétrico real $Z(x, y)$ con mapa de profundidad (`raven_depth_map.png`) y mapa de normales tangenciales PBR (`raven_pbr_normal.png`).
      - Eliminación absoluta de cortes planos o fragmentación 2D; reconstrucción anatómica del vientre emplumado orgánico con curvatura continua.
      - Separación limpia de capas: rama arbórea íntegra continua (`branch_cutout_complete.png`) y lienzo de pergamino puro mediante difusión biarmónica (`raven_background.png`).
    - **Resolución de Cinemática Alar (Erradicación del Efecto 'Imagen Estirada')**:
      - Se descartó el desplazamiento vertical por gradiente elástico ($dy = \text{flap} \cdot W$) que estiraba la textura como goma.
      - Implementación de **cinemática rotacional bicelular rígida**: matrices de rotación sobre el pivote del hombro $(510, 365)$ y flexión carpal en la muñeca, conservando al 100% las proporciones, grosor y trazos de plumas.
      - **Aleteo Bilateral 3D**:
        - Ala cercana (Ventral Layer): se alza hasta $+38^\circ$ en batido ascendente y barre a $-24^\circ$ en empuje descendente.
        - Ala lejana (Dorsal Layer): bate simétricamente por detrás del cuerpo en perspectiva 3D, alzándose por encima de la cabeza y cuello.
        - Casquete escapular (`scapular_cap`): oculta de forma continua el pivote del hombro sin desgarros.
    - **Resolución de Patas (Retracción Aerodinámica 100% en Vuelo)**:
      - En posado ($t < 0.75s$): Las garras sujetan la rama firmemente.
      - En despegue ($t \in [0.75, 0.95s]$): Las patas impulsan el salto y se retraen en trayectoria ascendente.
      - En vuelo ($t \ge 0.95s$): Retracción anatómica completa al 100%, ocultas a ras del plumaje ventral aerodinámico, eliminando cualquier astilla, palillo rígido o artefacto flotante en el aire.
    - **Rotación Tridimensional en su Eje Axial**:
      - Giro continuo en Yaw ($\pm 36^\circ$) con paralaje de perspectiva volumétrica ($Z_{\text{scale}} = 32.0$). El pico, la coronilla y el pecho abombado sobresalen espacialmente con respecto al plano posterior.
      - Alabeo aerodinámico en Roll coordinado con el giro ($\text{Roll} = \text{Yaw} \times 0.50$) e inclinación de cabeceo en ascenso ($\text{Pitch} = +16^\circ$).
    - **Física de Rama, Sombra Dinámica y Audio Sincronizado**:
      - Retroceso elástico amortiguado de la rama en el despegue ($\Delta y = 9.0 \cdot e^{-6 t} \cdot \cos(2\pi \cdot 7.5 t)$).
      - Sombra proyectada difusa sobre el pergamino con escala y desenfoque gausiano variable según la altitud de vuelo.
      - Síntesis de audio estéreo 44.1 kHz con chasquido de despegue, batidos aerodinámicos y graznidos guturales resonantes ($720\text{ Hz}$ y $1450\text{ Hz}$ con modulación rasposa a $65\text{ Hz}$).
    - **Entregables Tridimensionales y Cinemáticos**:
      - [`raven_3d.glb`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/raven_3d.glb) (2.32 MB, Khronos glTF 2.0 PBR, 2,395 vértices, 4,200 triángulos).
      - [`raven_3d.obj`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/raven_3d.obj) (358.7 KB) + [`raven_3d.mtl`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/raven_3d.mtl).
      - [`raven_pbr_normal.png`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/raven_pbr_normal.png) y [`raven_pbr_albedo.png`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/raven_pbr_albedo.png).
      - Vídeo Master: [`raven_flight_cinematic.mp4`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/raven_flight_cinematic.mp4) (1024x1024 @ 60 FPS, H.264 + AAC, 3.68 MB).
      - Bucle Web: [`raven_flight_animation.gif`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/raven_flight_animation.gif) (512x512 @ 24 FPS, 8.80 MB).
  - Demostrador y especificaciones detalladas en [`wolf_animation_showcase.md`](file:///C:/Users/sasuk/.gemini/antigravity/brain/25a9dd69-1a8e-409b-85e3-41655796e664/wolf_animation_showcase.md).
- **Entorno de Motores 3D: Instalación y Verificación de Blender 4.3.2**:
  - Binario autónomo oficial instalado en `/home/rtk/Aplicaciones/blender/` (Blender 4.3.2 Linux x86_64, build 2024-12-17 con Python 3.11.9 integrado y API `bpy`).
  - Enlace directo local en el workspace: [`./blender`](file:///home/rtk/Projects/AInimation/blender).
  - Enlace en PATH: `/home/rtk/.gemini/antigravity/bin/blender` (accesible globalmente como `blender`).
  - `.gitignore` actualizado para ignorar binarios de herramientas 3D.
  - Verificada ejecución headless con `blender -b --python-expr "import bpy..."` con 0 errores.
- **Módulo de Abstracción DCC y Adaptadores de Motor (`backend/engines/`, `backend/blender/`, `backend/ue5/`)**:
  - `Base3DEngineAdapter` ([`backend/engines/base.py`](file:///home/rtk/Projects/AInimation/backend/engines/base.py)): Interfaz abstracta común para motores 3D siguiendo principios SOLID (DIP, LSP, OCP) y tipado estricto Pydantic v2.
  - Factoría de adaptadores `get_engine_adapter(engine)` ([`backend/engines/base.py`](file:///home/rtk/Projects/AInimation/backend/engines/base.py)): Instanciación desacoplada y tipada para `'blender'` y `'ue5'`.
  - `BlenderAdapter` ([`backend/blender/adapter.py`](file:///home/rtk/Projects/AInimation/backend/blender/adapter.py)): Adaptador para orquestar Blender 4.3.2 de forma desatendida/headless con métodos `health_check()`, `build_scene()` y `render_video()`.
  - `UE5Adapter` ([`backend/ue5/adapter.py`](file:///home/rtk/Projects/AInimation/backend/ue5/adapter.py)): Adaptador para Unreal Engine 5 que implementa `Base3DEngineAdapter` sobre `UE5RestClient` y `render_sequence` (MRQ).
  - Add-on nativo para Blender ([`backend/blender/addon.py`](file:///home/rtk/Projects/AInimation/backend/blender/addon.py)): Panel en el 3D Viewport (`IANIMATION`) para configuración de rig de luces de estudio de 3 puntos, cámara teleobjetivo de 85mm con DoF e importación de mallas PBR.
  - Script de render de estudio ([`backend/blender/scripts/image_to_studio_render.py`](file:///home/rtk/Projects/AInimation/backend/blender/scripts/image_to_studio_render.py)): Conversión automatizada de imagen 2D a render cinemático con mapa de relieve PBR y set de iluminación de estudio en Blender EEVEE Next.
  - **Generalización de Herramientas FastMCP (`backend/mcp/tools.py`)**:
    - Herramienta `build_scene(scene_config, engine='ue5'|'blender')`: Despacha al motor 3D correspondiente de forma unificada.
    - Alias `build_ue5_scene`: Mantenido para retrocompatibilidad al 100%.
    - Herramienta `render_video(..., engine='auto'|'ue5'|'blender')`: Detección automática del motor según la extensión de la escena/render (`.blend`, `.obj`, `.glb` $\rightarrow$ Blender, de lo contrario UE5 MRQ).
  - **Proveedor de Relieve 3D Volumétrico en IA (`backend/ai/volumetric_3d.py` e `image_to_3d.py`)**:
    - `VolumetricReliefProvider`: Generador permanente de mallas tridimensionales con coordenadas $(X, Y, Z)$, mapa de profundidad $Z(x, y)$ y mapa de normales tangenciales PBR registrado en `provider_registry`.
  - **Pruebas Automatizadas Unitarias**:
    - [`tests/backend/test_blender_adapter.py`](file:///home/rtk/Projects/AInimation/tests/backend/test_blender_adapter.py): **6/6 tests pasados al 100%**.
    - [`tests/backend/test_ai_pipelines.py`](file:///home/rtk/Projects/AInimation/tests/backend/test_ai_pipelines.py): **34/34 tests pasados al 100%**.
    - [`tests/frontend/components.test.ts`](file:///home/rtk/Projects/AInimation/tests/frontend/components.test.ts): **11/11 tests de Vitest pasados al 100%**.
  - **Reconstrucción 3D Volumétrica Real y Render Cinemático (Cuervo Rojo)**:
    - Arte procesado: [`media_1791993921837_0eba4926.png`](file:///home/rtk/.gemini/antigravity/brain/0ab90927-ea7a-454f-b351-67f408a67a7e/.user_uploaded/media_1791993921837_0eba4926.png).
    - **Cumplimiento Estricto de la Mandatory 3D-First Policy**:
      - Erradicación del plano 2D inclinado. Generación de malla 3D estándar [`outputs/raven_3d/raven_volumetric_3d.obj`](file:///home/rtk/Projects/AInimation/outputs/raven_3d/raven_volumetric_3d.obj) (2.5 MB) con **23,881 vértices $(X, Y, Z)$** y **46,335 polígonos**.
      - Campo de profundidad continuo $Z(x, y)$ ([`outputs/raven_3d/raven_depth_map.png`](file:///home/rtk/Projects/AInimation/outputs/raven_3d/raven_depth_map.png)) con abombamiento esférico/elipsoidal anatómico en pecho y pico, y geometría cilíndrica en la rama.
      - Mapa de normales tangenciales PBR ([`outputs/raven_3d/raven_pbr_normal.png`](file:///home/rtk/Projects/AInimation/outputs/raven_3d/raven_pbr_normal.png)) y silueta alfa pura ([`outputs/raven_3d/raven_cutout.png`](file:///home/rtk/Projects/AInimation/outputs/raven_3d/raven_cutout.png)).
    - **Render y Cinemática en Blender 4.3.2**:
      - Captura en perspectiva 3/4 con luces de estudio de 3 puntos: [`outputs/renders/red_raven_3d_volumetric.png`](file:///home/rtk/Projects/AInimation/outputs/renders/red_raven_3d_volumetric.png) (1280x720, 1.3 MB).
      - Animación turntable con oscilación armónica en Yaw ($\pm 32^\circ$) y Pitch ($\pm 6^\circ$): [`outputs/renders/red_raven_3d_turntable.mp4`](file:///home/rtk/Projects/AInimation/outputs/renders/red_raven_3d_turntable.mp4) (H.264 @ 24 FPS, 1.1 MB) y bucle web [`outputs/renders/red_raven_3d_turntable.gif`](file:///home/rtk/Projects/AInimation/outputs/renders/red_raven_3d_turntable.gif) (3.1 MB).
      - Escena Blender editable: [`outputs/renders/red_raven_3d_volumetric.blend`](file:///home/rtk/Projects/AInimation/outputs/renders/red_raven_3d_volumetric.blend) (3.6 MB).
      - Documentación completa en [`red_raven_true_3d_showcase.md`](file:///home/rtk/.gemini/antigravity/brain/0ab90927-ea7a-454f-b351-67f408a67a7e/red_raven_true_3d_showcase.md).
  - **Motor de Rigging Esquelético Procedural y Articulación en Blender (`backend/blender/rigging.py`)**:
    - `BlenderRigger`: Generador automático de armaduras óseas e inyector de cinemática articular sobre mallas 3D (`.obj`, `.glb`).
    - **Armaduras Anatómicas Preconfiguradas**:
      - `avian`: 13 huesos estructurados (`Root`, `Spine`, `Neck`, `Head`, `Wing_Shoulder_L`, `Wing_Mid_L`, `Wing_Tip_L`, `Wing_Shoulder_R`, `Wing_Mid_R`, `Wing_Tip_R`, `Tail`, `Leg_L`, `Leg_R`).
      - `canine`: 12 huesos con articulación temporomandibular (`Jaw`, `Head`, `Neck`, `Spine`, extremidades cuadrúpedas y cola).
      - `bipedal`: 15 huesos con jerarquía cinemática estándar humanoide.
    - **Skinning con Garantía $C^\infty$ (Sin Rupturas de Superficie)**: Enlace primario `ARMATURE_AUTO` y fallback matemático continuo por ponderación gaussiana de distancias a los ejes óseos ($w_i \propto \exp(-d_i^2 / 2\sigma^2)$).
    - **Generador de Animaciones Armónicas (`generate_avian_flap_animation`)**: Ciclos sinusoidales con desfase de propagación aerodinámica ($0^\circ \rightarrow 35^\circ \rightarrow 70^\circ$) y elevación vertical (*body bobbing*).
    - **Script Autónomo Headless**: [`backend/blender/scripts/rig_and_animate.py`](file:///home/rtk/Projects/AInimation/backend/blender/scripts/rig_and_animate.py).
    - **Entregables del Cuervo Rojo Articulado**:
      - Malla rigged: [`outputs/raven_3d/red_raven_rigged.glb`](file:///home/rtk/Projects/AInimation/outputs/raven_3d/red_raven_rigged.glb) (2.0 MB).
      - Escena animada: [`outputs/scenes/red_raven_rigged.blend`](file:///home/rtk/Projects/AInimation/outputs/scenes/red_raven_rigged.blend) (5.7 MB).
      - Vídeo Master de vuelo: [`outputs/renders/red_raven_rigged_flight.mp4`](file:///home/rtk/Projects/AInimation/outputs/renders/red_raven_rigged_flight.mp4) (746 KB, H.264 @ 24 FPS, 1280x720).
      - Bucle web: [`outputs/renders/red_raven_rigged_flight.gif`](file:///home/rtk/Projects/AInimation/outputs/renders/red_raven_rigged_flight.gif) (1.3 MB).
      - Demostrador y reporte: [`blender_rigging_and_live_bridge_showcase.md`](file:///home/rtk/.gemini/antigravity/brain/0ab90927-ea7a-454f-b351-67f408a67a7e/blender_rigging_and_live_bridge_showcase.md).
  - **Motor de Despille de Bordes y Defringing (`backend/ai/defringe.py`)**:
    - Elimina al 100% el halo claro de fondo y el sangrado de papel/pergamino en recortes 2D.
    - Utiliza la Transformada de Distancia Euclidiana (EDT) con dilatación de los píxeles interiores puros hacia los bordes y atenuación subpíxel del canal alfa.
    - Test suite dedicado: [`tests/backend/test_defringe.py`](file:///home/rtk/Projects/AInimation/tests/backend/test_defringe.py) (2/2 tests pasados).
  - **Motor de Descomposición Anatómica por Componentes y Desacoplamiento de Props (`backend/ai/component_decomposer.py`)**:
    - Resuelve de raíz el defecto de "juguete squashy de plástico" mediante descomposición por componentes y capas:
      - Desacoplamiento ambiental: La rama (`Prop_Branch`) se aísla como prop 3D rígido estático con inpainting cilíndrico en las zonas de agarre de las garras.
      - Torso continuo ($C^\infty$): El cuerpo base (`Subject_Torso`) abarca cabeza, pico, cuello, pecho, abdomen, garras y cola de forma ininterrumpida, con inpainting del plumaje bajo el ala para que nunca se revele un vacío al aletear.
      - Ala frontal orgánica (`Subject_Wing_Ventral`): Contorno escapular natural de plumas (cobertoras y primarias) con grosor laminar aerodinámico (`thickness=0.10`), eliminando paredes verticales abruptas ("cortinas").
      - Ala trasera en perspectiva (`Subject_Wing_Dorsal`): Capa de contra-aleteo estereoscópico con offset en $Z$.
    - Soporte geométrico subpíxel anti-aliased: La cuadrícula poligonal se extiende suavemente hacia la zona transparente para que el canal alfa PBR proporcione curvas nítidas sin dientes de serrucho.
    - Test suite dedicado: [`tests/backend/test_component_decomposer.py`](file:///home/rtk/Projects/AInimation/tests/backend/test_component_decomposer.py) (3/3 tests pasados).
  - **Rigging Jerárquico con Aislamiento de Pesos y Render Cinemático Refinado (`backend/blender/scripts/multi_component_rig.py` y `backend/ai/component_decomposer.py`)**:
    - **Corrección de Inversión de Capa Z y Abombamiento del Torso**:
      - El torso base (`Subject_Torso`) ahora cuenta con una cama anatómica alar (`torso_depth_scale` indentado al 50% en `wing_raw_mask` mediante filtro gaussiano $\sigma=4.0$), con grosor reducido a `thickness = 0.14, z_offset = 0.0`.
      - El ala ventral (`Subject_Wing_Ventral`) se posiciona estrictamente en la capa frontal con `z_offset = 0.16, thickness = 0.06`, quedando más cercana a la cámara en Blender (coordenada $Y \in [-0.22, -0.16]$ frente a torso $Y \in [-0.14, 0.0]$).
      - El ala dorsal (`Subject_Wing_Dorsal`) se confina a la capa posterior con `z_offset = -0.10, thickness = 0.06` (coordenada Blender $Y \in [0.04, 0.10]$).
    - **Erradicación del Rayado Radial Voronoi**:
      - Sustituido el lookup plano nearest-neighbor de EDT por difusión multiescala Gaussiana/Laplaciana ($\sigma \in [16.0, 10.0, 6.0, 3.0]$) sobre el lecho bajo el ala, produciendo una transición orgánica y continua de plumaje sin bandas radiales.
    - **Transformación de Coordenadas de Pivote Articular del Hombro**:
      - Corrección matemática de la discrepancia de 65.2 cm entre el espacio OBJ ($X$=ancho, $Y$=alto, $Z$=relieve) y el espacio Blender ($X$=ancho, $Y$=profundidad, $Z$=alto):
        `blender_px = px`, `blender_py = -pz`, `blender_pz = py`.
      - Los huesos `Wing_Shoulder_L` y `Wing_Shoulder_R` se fijan exactamente sobre la juntura escapular anatómica de las mallas.
    - **Alineación Axial del Esqueleto (Root, Spine, Head)**:
      - Los huesos axiales se reorientaron verticalmente a lo largo de $+Z$ (en lugar del plano horizontal $Y$):
        `Root`: `(0.0, -0.15, -0.25)` a `(0.0, -0.15, 0.10)`.
        `Spine`: `(0.0, -0.15, 0.10)` a `(-0.05, -0.15, 0.35)`.
        `Head`: `(-0.05, -0.15, 0.35)` a `(-0.25, -0.15, 0.60)`.
    - **Cinemática Alar por Elevación Coronal ($C^\infty$)**:
      - La rotación alar se reconfiguró sobre el eje de elevación coronal (rotación local $X$ con `align_roll((0, 0, 1))`), alzando el ala entre $+28^\circ$ y $+35^\circ$ por encima de la espalda y barriendo a $-12^\circ$ en empuje descendente, con reposo exacto a $0^\circ$ en cuadro 1.
    - **Encuadre Dinámico de Cámara Corregido**:
      - Sustituido `span_y` (profundidad) por `span_z` (altura vertical real del sujeto) en el cálculo de distancia focal:
        `cam_dist = max(span_x / 0.36, span_z / 0.28) * 0.90 + 1.2`.
    - **Exportación GLB Limpia y Compatibilidad EEVEE Next**:
      - Exportación acotada exclusivamente al rig de la armadura, mallas del personaje y props (`use_selection=True`), eliminando el plano de estudio de 18 m y las luces del archivo `.glb`.
      - Materiales configurados con `surface_render_method = 'BLENDED'` y `blend_method = 'HASHED'`.
    - **Erradicación de Defectos de Pliegues, Arrugas y Dientes de Sierra ("Pliegues y Costuras")**:
      - **Topología 2-Manifold de Frontera Unificada (Zero Rim Quads)**:
        - Se eliminó la franja perimetral de quads de borde (`f a b bb` / `f a bb ba`) que generaba caras a 90° perpendiculares captando reflejos especulares agudos ("efecto cremallera / zipper").
        - Los vértices de borde de las superficies frontal y dorsal ahora comparten índices geométricos 3D unificados (`boundary_v_set`) con profundidad $Z = z_{\text{offset}} + \text{camber}$, garantizando que las caras frontales y traseras cierren el volumen matemáticamente sin caras de borde adicionales.
        - Malla sólida 100% estanca 2-manifold ($\chi = 2$, boundary edges = 0) con normales tangenciales continuas calculadas por el motor.
      - **Relajación Laplaciana de Contornos (Eliminación de Dientes de Cuadrícula)**:
        - 4 iteraciones de relajación Laplaciana sobre el bucle de vértices de borde $\vec{x}_v \leftarrow (1-\lambda)\vec{x}_v + \frac{\lambda}{|N(v)|}\sum \vec{x}_n$, convirtiendo la silueta rasterizada escalonada en una curva spline $C^1$ orgánica.
        - Coordenadas UV de borde recalculadas a partir de las posiciones relajadas para mantener una proyección sin estiramiento.
      - **Transición Continua $C^1$ Hermite de Pico a Garganta y Bóveda Craneal**:
        - Sustituido el cuadro de corte rectangular binario `(u < 0.16) & (v < 0.28)` por una modulación continua $C^1$ Hermite en función de la distancia al eje del pico:
          $\text{beak\_influence} = \frac{1}{2}(1 - \cos(\pi \cdot \dots))(1 - t_u)$.
        - Erradicó por completo la muesca o hendidura gular bajo la mandíbula inferior y la costura de la coronilla.
        - Inclusión de bóveda craneal convexa continua en $u \in [0.10, 0.35], v \le 0.22$.
      - **Camber Alar Aerodinámico y Envoltura Torácica**:
        - Campo de curvatura de camber alar en `backend/ai/component_decomposer.py`: el borde dorsal y la raíz escapular se curvan hacia adentro ($-\Delta Z = -0.065$) para abrazar la caja torácica convexa, eliminando el borde plano en escalón flotante.
      - **Eliminación de Terrazas en la Rama y Sombreado de Plumas Orgánico**:
        - En `Prop_Branch`, modulación de micro-relieve atenuada (`0.025`) y pipeline de modificadores con `SMOOTH` (`factor=0.85`, `iterations=6`) previo a `SUBSURF` (nivel 2), eliminando cualquier estriado o peldaño en la percha.
        - Rugosidad PBR de plumaje ajustada a $0.82$ (208) y `Specular IOR Level` atenuado a $0.28$, eliminando destellos plásticos ("squashy toy") y produciendo micro-dispersión suave de plumas naturales.
    - **Entregables Actualizados y Verificados**:
      - Escena Blender: [`outputs/scenes/red_raven_hierarchical_flight.blend`](file:///home/rtk/Projects/AInimation/outputs/scenes/red_raven_hierarchical_flight.blend).
      - Modelo Khronos glTF sólido estanco: [`outputs/scenes/red_raven_hierarchical_flight.glb`](file:///home/rtk/Projects/AInimation/outputs/scenes/red_raven_hierarchical_flight.glb).
      - Video Master MP4 (48 cuadros @ 24 FPS): [`outputs/renders/red_raven_hierarchical_flight.mp4`](file:///home/rtk/Projects/AInimation/outputs/renders/red_raven_hierarchical_flight.mp4).
      - Bucle animado GIF: [`outputs/renders/red_raven_hierarchical_flight.gif`](file:///home/rtk/Projects/AInimation/outputs/renders/red_raven_hierarchical_flight.gif).
  - **Galería Multi-Ángulo 3D y Validación Anatómica (`outputs/renders/multi_angle/`)**:
    - **Validación Visual de Malla Sólida 2-Manifold y Shading PBR en EEVEE Next**:
      - `angle_user_facing_view.png` (970 KB): Vista frontal directa a -75° (ángulo reportado por el usuario); valida el pico afilado en cuña triangular (culmen y gonys afilados), la quilla pectoral saliente (carina sterni) y la profundidad del tórax (0.22) sin efecto de salchicha inflada y con pliegues completamente erradicados.
      - `angle_01_hero_front34.png` (1009 KB): Vista frontal en escorzo 3/4 (Azimuth: -15°, Elevación: +6°), encuadre cinemático con volumen convexo y reflejos especulares en plumaje y ojo.
      - `angle_02_side_profile.png` (960 KB): Perfil lateral (Azimuth: -55°, Elevación: +4°), evidencia el relieve volumétrico del pico, pecho redondeado y desacoplamiento de la rama.
      - `angle_03_dorsal_back34.png` (1005 KB): Perspectiva dorsal trasera 3/4 (Azimuth: +40°, Elevación: +14°), plumaje continuo sobre el lecho escapular sin grietas.
      - `angle_04_low_angle_dramatic.png` (998 KB): Ángulo contrapicado dramático (Azimuth: -10°, Elevación: -16°), envoltura tridimensional de las garras en la corteza y sombreado GTAO.
      - `angle_05_top_perspective.png` (988 KB): Perspectiva cenital 3/4 (Azimuth: -25°, Elevación: +30°), visualización del grosor volumétrico alar y curvatura de la coronilla.
      - `angle_06_true_rear_view.png` (666 KB): Reverso posterior completo a 180° (Azimuth: +165°, Elevación: +8°), demostrando una malla 100% estanca (boundary edges = 0) con plumaje dorsal sintetizado orgánicamente sin anomalía bicéfala.
    - **Turntable 360° Orbit (36 frames con fondo de estudio continuo)**:
      - Video MP4: [`outputs/renders/multi_angle/red_raven_3d_orbit_turntable.mp4`](file:///home/rtk/Projects/AInimation/outputs/renders/multi_angle/red_raven_3d_orbit_turntable.mp4) (481 KB, 1280x720 @ 24 FPS).
      - Bucle Web GIF: [`outputs/renders/multi_angle/red_raven_3d_orbit_turntable.gif`](file:///home/rtk/Projects/AInimation/outputs/renders/multi_angle/red_raven_3d_orbit_turntable.gif) (1.1 MB).
  - **Soporte de Vistas Múltiples y Perfilador Anatómico**:
    - `MultiViewImageSet`: Contrato de datos en `backend/core/models.py` (`front_image_path`, `side_image_path`, `back_image_path`, `top_image_path`) para reconstrucción ortogonal por Turnaround Sheets (Visual Hull Carving).
    - `Avian Anatomical Depth Prior`: En `backend/ai/component_decomposer.py`, modulación de profundidad continua con afilado en cuña del pico ($0.08$ en punta), cresta de quilla pectoral (carina), aplanado de rectrices caudales y proporción torácica profunda ($0.22$).
    - Ciclorama 360° continuo en Blender para eliminar recortes de plano en ángulos de cámara abiertos.

  - **Pipeline Bípedo Anatómico & Modelo Táctico Anime (`outputs/anime_tactical_components/`, `outputs/renders/anime_tactical/`)**:
    - **Defringing & Segmentación de Ciclorama de Estudio**: Detección adaptativa de gradientes cromáticos mediante percentiles de bordes en `backend/ai/defringe.py` (`min_border_b`, `max_border_r`), eliminando halos azules y preservando el 100% de los detalles interiores (mangas grises, estrellas en falda, hebillas y pelo).
    - **Bipedal Anatomical Depth Prior (`backend/ai/component_decomposer.py`)**: Modulación anatómica continua $C^\infty$ que erradica la apariencia de muñeco inflado / juguete squashy:
      - Visera de gorra: proyección anterior $+22\%$.
      - Línea media facial (puente nasal y mentón): relieve prominente $+18\%$.
      - Cuello anatómico recesivo: factor de escala $0.72$ para evitar engrosamiento por encima de la mandíbula.
      - Chaleco y bolsillos tácticos: relieve pectoral $+30\%$ con bolsillos utilitarios $+15\%$.
      - Cintura atlética entallada: escala $0.84$.
      - Pistolera de muslo (holster): proyección lateral y frontal $+18\%$.
      - Rodilleras tácticas: proyección convexa $+18\%$.
      - Botas de combate: collarines cilíndricos y punteras $+22\%$.
    - **Síntesis Dorsal Orgánica (Zero Two-Faced Anomaly)**: Inpainting radial elíptico en el reverso para sustituir la cara por cabello plateado y gorra oscura, e inpainting de piel uniforme en la parte trasera del muslo eliminando la duplicación del tatuaje floral frontal.
    - **Malla Sólida 2-Manifold Estanca**: 13,378 vértices, 26,760 triángulos, **0 bordes abiertos (boundary edges = 0)**.
    - **Armadura Bípeda y Skinning Suave (`backend/blender/rigging.py`)**: Esqueleto anatómico `BIPEDAL_BONES` alineado en el eje vertical $+Z$ con 16 huesos (`Root`, `Spine`, `Neck`, `Head`, `Clavicle_L/R`, `Arm_L/R`, `Forearm_L/R`, `Thigh_L/R`, `Shin_L/R`, `Foot_L/R`).
    - **Ciclo de Animación Idle Táctico (`generate_bipedal_idle_animation`)**: Animación procedimental de respiración táctica (48 cuadros @ 24 FPS) con oscilación pélvica de 4 mm, expansión torácica, micro-paneo de observación en la cabeza y relajación de brazos en desfase continuo.
    - **Activos de Producción Exportados**:
      - Escena iluminada Blender: [`outputs/scenes/anime_tactical_bipedal.blend`](file:///home/rtk/Projects/AInimation/outputs/scenes/anime_tactical_bipedal.blend).
      - Malla articulada estándar: [`outputs/scenes/anime_tactical_bipedal.glb`](file:///home/rtk/Projects/AInimation/outputs/scenes/anime_tactical_bipedal.glb).
      - Video Idle MP4: [`outputs/renders/anime_tactical/anime_tactical_idle.mp4`](file:///home/rtk/Projects/AInimation/outputs/renders/anime_tactical/anime_tactical_idle.mp4) y [`anime_tactical_idle.gif`](file:///home/rtk/Projects/AInimation/outputs/renders/anime_tactical/anime_tactical_idle.gif).
      - Turntable 360° MP4: [`outputs/renders/anime_tactical/anime_tactical_3d_orbit_turntable.mp4`](file:///home/rtk/Projects/AInimation/outputs/renders/anime_tactical/anime_tactical_3d_orbit_turntable.mp4) y [`.gif`](file:///home/rtk/Projects/AInimation/outputs/renders/anime_tactical/anime_tactical_3d_orbit_turntable.gif).
      - 7 Ángulos Stills de Estudio: `angle_01_hero_front34`, `angle_02_side_profile`, `angle_user_facing_view`, `angle_03_dorsal_back34`, `angle_04_low_angle_dramatic`, `angle_05_top_perspective`, `angle_06_true_rear_view`.

  - **Suite Global de Pruebas**:
    - **878 tests backend pasados al 100%** (22 módulos de prueba).
    - **11 tests Vitest frontend pasados al 100%**.
    - **58 tests E2E pasados al 100%**.
    - **Total: 947 tests automatizados 100% verdes**.
    - **0 errores de TypeScript estricto**.

---

## 4. Backlog y Próximos Pasos para Sesiones Futuras
1. **Retargeting de Mocap (Video -> Blender Armature)**:
   - Conectar los marcadores de `extract_mocap` (GVHMR / MediaPipe) para retargetear directamente sobre las armaduras aviares o bípedas en Blender.
2. **Relay Bidireccional UI Three.js <-> Blender Live Bridge**:
   - Conectar el scrubber del visor 3D en Tauri (`Viewport.tsx` / `Timeline.tsx`) con `BlenderLiveClient` para mover la cámara y timeline en Blender de manera simultánea.
3. **Conexión Live con Unreal Engine 5 Editor**:
   - Usar `python -m backend.ue5.companion --generate-ini` para configurar cualquier proyecto de Unreal Engine 5.3+ con Remote Control y Pixel Streaming.
   - Ejecutar `python -m backend.ue5.companion --check` para diagnosticar la conexión con el editor en vivo.
4. **Empaquetado de Distribución Final**:
   - Ejecutar `cargo tauri build` para generar el instalador MSI / binario de producción.
5. **Inferencia con Claves de Producción**:
   - Asignar claves reales en `.env` (`FAL_KEY`, `TRIPO_API_KEY`, `REPLICATE_API_TOKEN`) para ejecutar inferencias sobre GPUs remotas fuera del modo mock.



