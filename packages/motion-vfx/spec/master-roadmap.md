# Hoja de Ruta Maestra: Motor de Video, Motion Graphics y Generación Autónoma por IA

**Documento:** `spec/master-roadmap.md`  
**Estado:** VIGENTE / NORMATIVO  
**Objetivo Estratégico:** Construir un motor modular y determinista de edición de video corto (TikTok, YouTube Shorts, Reels), estructurado en capas limpias desde las primitivas audiovisuales hasta la planificación semántica por agentes LLM.

---

## 🗺️ Mapa Integral de Capas y Fases

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             CAPA 7: IA & PLANIFICACIÓN                           │
│  7A: AI Command  • 7B: Video DSL • 7C: AI Planner • 7D: Tools • 7E: Correction   │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────┴─────────────────────────────────────────┐
│                      CAPA 6: MODELO SEMÁNTICO & MOTION PRESETS                   │
│  6A: Templates • 6B: Presets • 6C: Procedural • 6D: Beats • 6E: Reframing        │
│  6F: Editing Intelligence • 6G: Semantic Video Model                             │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────┴─────────────────────────────────────────┐
│                           CAPA 5: MOTOR DE EDICIÓN DE VIDEO                      │
│  5A: Media/Assets [✅]  • 5B: Video Timeline [✅]  • 5C: Scenes & Transitions [⏳] │
│  5D: Audio Engine      • 5E: Captions Engine      • 5F: Advanced Typography      │
│  5G: Masks & Tracking  • 5H: Camera System        • 5I: Advanced Effects         │
│  5J: Render Pipeline                                                             │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────┴─────────────────────────────────────────┐
│                 CAPAS 1-4: CORE TEMPORAL, ANIMACIONES & EFECTOS [✅]             │
│  1.0-2C: Core Temporal, Affine 2D, Element Model, Serialization & Validation     │
│  3A-3E: Animation Trees, Basic/Advanced Motion, Composition Nodes, DSL           │
│  4A-4C: Preset Architecture, Kinetic Typography Subtargets, Effects Stack        │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Desglose Detallado por Fase

### 🎬 Bloque 5.x — Motor de Edición de Video (Video Engine Core)
- **5A. Media / Asset System [✅]:** Ingesta de archivos reales (`.mp4`, `.png`, `.wav`, `.ttf`, `.svg`), metadatos, hashing SHA-256, `FrameCache` LRU y mapping temporal.
- **5B. Video Timeline & Multi-Track NLE [✅]:** Pistas multi-canal (`video`, `audio`, `graphics`), clips $[start, end)$, velocidades, Z-order, marcadores y operaciones `splitClip()`, `trimClip()`, `moveClip()`.
- **5C. Scenes & Transitions [⏳ EN CURSO]:** Transiciones compuestas entre tomas (`Cut`, `CrossDissolve`, `Zoom`, `WhipPan`, `Blur`, `Flash`, `Glitch`, `MatchCut`) sobre solapamientos de clips.
- **5D. Audio Engine:** Formas de onda (`waveform`), mezcla multi-canal, envelopes de volumen, paneo, ecualización y ducking automático ante voz.
- **5E. Subtitle / Caption Engine:** Generación y renderizado de subtítulos sincronizados palabra por palabra con tracking temporal y estilos para redes.
- **5F. Advanced Text & Typography:** Auto-wrap, alineación dinámica, kinetic typography con word highlights e integración tipográfica vectorial.
- **5G. Masks / Rotoscoping / Tracking:** Máscaras de Bezier animables, Track Mattes (Alpha/Luma), clipping paths e interpolación de rotoscopía.
- **5H. Camera & Motion System:** Cámara 2D/3D con control de encuadre, Pan, Dolly, Zoom focal y sacudidas deterministas (`camera shake`).
- **5I. Advanced Effects:** Distorsión por desplazamiento, aberración cromática, LUTs de color grading, estilizado VHS y desenfoque por profundidad (*depth blur*).
- **5J. Rendering / Export Pipeline:** Planificador concurrente de fotogramas, compositor GPU/CPU y exportador a video (`.mp4`, `.webm`, `.mov`, `.gif`).

---

### 🎨 Bloque 6.x — Motion Graphics & Modelo Semántico
- **6A. Composition / Template System:** Plantillas modulares reutilizables con slots dinámicos de texto, imagen y video.
- **6B. Motion Preset System:** Biblioteca de presets composibles y parametrizables de texto, transiciones y efectos visuales.
- **6C. Procedural Graphics:** Generación procedural de fondos animados, partículas, barras de progreso y formas abstractas.
- **6D. Beat / Audio Analysis:** Detección automática de BPM, transitorios de percusión y alineación rítmica de cortes.
- **6E. Auto-Reframing:** Adaptación inteligente de relaciones de aspecto (16:9 a 9:16 vertical) con seguimiento del sujeto principal.
- **6F. Editing Intelligence:** Heurísticas de ritmo visual, detección de silencios para corte dinámico (*jump cuts*) y pacing.
- **6G. Semantic Video Model:** Abstracción conceptual de elementos (`person`, `background`, `speaker`, `product`, `hook`, `keyword`, `scene`).

---

### 🤖 Bloque 7.x — Capa de Orquestación e Inteligencia Artificial
- **7A. AI Command Layer:** API imperativa de alto nivel para manipulación mediante agentes (`addClip`, `animateText`, `focusSubject`).
- **7B. Video DSL:** Lenguaje declarativo estructurado JSON para representar proyectos completos en prompts de LLMs.
- **7C. AI Planning Engine:** Motor de razonamiento de guion a storyboard y desglose secuencial de escenas.
- **7D. Tool / Action System:** Herramientas y funciones estructuradas para integración con modelos multimodales.
- **7E. Validation & Self-Correction:** Diagnósticos automáticos de colisiones temporales, clips vacíos o parámetros inconsistentes.

---

### 🔌 Bloque 8.x — Integración y Conectores Externos
- **8A. MCP Adapter:** Protocolo Model Context Protocol para interactuar nativamente con Claude, Gemini y herramientas IDE.
- **8B. Editor Integration:** Adaptadores para previsualización interactiva en navegadores y entornos de edición.
- **8C. After Effects Adapter:** Exportador de scripts JSX y composiciones `.aep` compatibles con Adobe After Effects.
- **8D. DaVinci / Premiere Adapters:** Exportación a formatos universales XML / EDL / FCPXML.
- **8E. Headless Rendering:** Modo de renderizado autónomo en servidores cloud sin entorno gráfico.

---

### ⚡ Bloque 9.x & 10 — Rendimiento, Escala y Producción
- **9A. Performance & Profiling:** Optimización de cuello de botella temporal.
- **9B. GPU Acceleration:** Aceleración por shaders WebGL/WebGPU/Metal.
- **9C. Intelligent Caching:** Caché multi-nivel en memoria y disco.
- **9D. Parallel Rendering:** Renderizado distribuido por chunks de fotogramas.
- **10. Production Hardening:** Blindaje de estabilidad, tests de estrés e invariancia para producción continua.
