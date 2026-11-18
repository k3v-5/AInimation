# Motion Graphics & Autonomous Video Editorial Engine: Guía Maestra y Estado Global

> **Audiencia del Documento:** Ingenieros de software, diseñadores de motion graphics, directores de postproducción y Agentes de Inteligencia Artificial que se incorporen al repositorio sin contexto previo.  
> **Versión Actual del Motor:** `v4.0.0-editorial-master`  
> **Nivel de Certificación:** **Level 5 Production Certified** (21 Production Gates aprobados)  
> **Batería de Pruebas Automatizadas:** **1,322 pruebas al 100% en verde** en 455 suites / archivos de prueba (`node:test`).

---

## 1. ¿Qué es este Proyecto y qué Problema Resuelve?

### El Problema de Fondo
Los Modelos de Lenguaje Grande (LLMs) destacan analizando texto e ideas abstractas, pero son intrínsecamente malos editando vídeo directamente:
- **Alucinación temporal:** Los LLMs confunden números de fotogramas, calculan mal los solapamientos de capas y generan cortes desincronizados.
- **Incompatibilidad de software:** Herramientas profesionales como **Adobe After Effects**, **DaVinci Resolve** o **Premiere Pro** requieren código exacto (ExtendScript JSX, OTIO, XML) con jerarquías estrictas de composición, curvas Bézier matemáticas y matrices de transformación espacial 2D/3D.
- **Falta de criterio editorial:** Un corte de vídeo no es solo cortar cuando termina una frase; requiere ritmo, alternancia dramática de tensiones, control de saturación mental del espectador y respeto estricto a la gramática cinematográfica (eje de 180°, continuidad de mirada, iluminación y sonido ambiente).

### La Solución de este Motor
Este proyecto es una **Plataforma de Producción Audiovisual Autónoma y Determinista** controlada por Inteligencia Artificial a través del protocolo **MCP (Model Context Protocol)**, interfaces de línea de comandos (**CLI**) y un **DSL declarativo** en TypeScript.

El motor actúa como el **Director Técnico y Editor Jefe** entre la IA y After Effects:
1. La IA expresa su intención de alto nivel (guion, estilo editorial, metraje disponible, idiomas de entrega).
2. El motor compila esa intención en una **Representación Intermedia Editorial (IR)** matemáticamente verificada.
3. El motor ejecuta simulaciones de atención humana, carga cognitiva, verificación de evidencias y continuidad de plano.
4. Finalmente, transpila el resultado en scripts **ExtendScript JSX** ejecutables directamente en After Effects o exportables a formatos universales (EDL, FCPXML, OTIO).

---

## 2. Principios Arquitectónicos Inviolables

1. **Determinismo Criptográfico Estricto:**
   - A idénticos inputs y versiones de runtime/renderer, el motor produce **el mismo IR, timecodes, parámetros de composición y artefactos de compilación**. Para garantizar renders finales bit-identical se requiere además fijar explícitamente: versión de renderer (After Effects / aerender), backend de GPU, versión de códecs/FFmpeg, perfiles de gestión cromática y versiones de fuentes tipográficas.
   - Todo plan de montaje, trailer o reporte emite una firma inmutable **SHA-256 calculada sobre JSON Canónico** (claves ordenadas lexicográficamente, redondeo numérico fijo, rechazo estricto de `NaN`/`Infinity`).
2. **Representación Intermedia (IR) como Única Fuente de Verdad:**
   - Los archivos brutos de vídeo/audio jamás se modifican directamente (no destructividad).
   - Toda decisión de corte o animación se modela como un grafo de transformaciones $IR \to IR$ desacoplado de cualquier software propietario.
3. **Verificación en 7 Capas:**
   - La suite de pruebas abarca: Unit Tests, Integration Tests, Mathematical Invariant Tests, Serialization Tests, **Property-Based Testing (PBT con `fast-check`)**, Golden Regression Tests y Conformance Tests.
   - **Regla de Oro:** Prohibido relajar o borrar aserciones de pruebas existentes para "hacer pasar" código nuevo. Las 1,004 pruebas deben estar siempre en verde.
4. **Offline First & Costo Computacional Cero:**
   - La síntesis de voz multilingüe (Piper TTS), transcripción (Whisper local) y síntesis acústica de efectos (SoundBank WAV) se ejecutan de forma local y soberana, sin dependencias de APIs de pago externas obligatorias.
5. **Estilo Visual Maestro (TIME Editorial / Poster Style):**
   - Tipografía condensada mayúscula ultra-bold (`Impact`, `Arial Black`, `Anton`), tracking negativo, contraste cromático de alto impacto (rojo carmesí `#FF1424` sobre blanco puro y fondos oscuros), animación palabra por palabra sincronizada con la fonética y desenfoque de movimiento nativo (`comp.motionBlur = true`).

---

## 3. Mapa de Arquitectura Global

```
                                    ENTRADA DEL SISTEMA
             ┌───────────────────────────────┼───────────────────────────────┐
             ▼                               ▼                               ▼
       Servidor MCP                 Declarative DSL                   CLI Standalone
     (39+ Herramientas)            (ProductionDSL.ts)          (motion-engine, vlog:produce)
             │                               │                               │
             └───────────────────────────────┬───────────────────────────────┘
                                             ▼
                             NÚCLEO DEL MOTOR EDITORIAL v4.0
             ┌───────────────────────────────────────────────────────────────┐
             │  • KnowledgeGraph & Scene Graph (Ontologías de Metraje)       │
             │  • Narrative Arc Engine (10 Beats Canónicos Documentales)     │
             │  • EvidenceEngine (Auditoría de Afirmaciones y Citaciones)    │
             │  • ArchivalMediaEngine (Animación 2D Ken Burns y Licencias)   │
             │  • CreditsCompiler (Lower-Thirds TIME y Rodillo Final)        │
             │  • TrailerGenerator & SocialHookScorer (Teasers y Retención)  │
             │  • MatchCutEngine (Correspondencias Visuales y Cinéticas)     │
             │  • AudienceAttentionModel & CognitiveLoadEngine (Psicología)  │
             │  • EditorialContrast & PacingCurveComposer (Ritmo y Tensión)  │
             └───────────────────────────────┬───────────────────────────────┘
                                             ▼
                          IR EDITORIAL (Representación Intermedia)
                                             │
             ┌───────────────────────────────┼───────────────────────────────┐
             ▼                               ▼                               ▼
      ExtendScript JSX              Final Cut Pro XML                Paquete Social
   (Adobe After Effects)           (DaVinci / Premiere)       (9:16, 16:9, 1:1, Miniaturas)
```

---

## 4. Dónde Estamos Hoy: Inventario de lo Construido al 100%

### Hito A: Fundación del Motor & Core Engine (v1.0 – v3.0) — Fases 1 a 27
- **Línea Temporal & Keyframing:** Curvas de interpolación Bézier cúbica deterministas, normalización de tiempo flotante con tolerancia $\epsilon \le 10^{-10}$.
- **Geometría & Safe Zones:** Detección de zonas seguras de pantalla para plataformas sociales (Instagram Reels, TikTok, YouTube Shorts), evitando solapamientos con la interfaz gráfica de usuario (UI exclusion zones).
- **Control de Transacciones & Rollback:** Capacidad de revertir modificaciones en el proyecto ante errores inesperados mediante snapshots criptográficos en memoria.
- **Security Sandbox:** Ejecución aislada de scripts After Effects con validación estricta de rutas en el sistema de archivos.

### Hito B: Autonomous Content Factory (v3.4.0)
- **Whisper Local:** Transcripción automática offline de audio a texto con timestamps fonéticos fotograma a fotograma.
- **Viral Clipper & Reframe:** Scoring algorítmico de retención de audio para extraer automáticamente micro-clips verticales (Shorts) a partir de grabaciones largas horizontales.
- **15 Motores de Estilo:** Presets configurables de creadores destacados (Ali Abdaal, Vox Media, TIME Insignia, Hormozi, MrBeast, etc.).
- **SoundBank Procedural:** Síntesis matemática de efectos de sonido WAV (16-bit / 44.1kHz mono): risers, whooshes, impacts, pops y sub-bass drops.

### Hito C: Vlog Expansion Suite (v3.5.0)
- **Orquestador DAG de 22 Fases:** Pipeline completo de ingesta, clasificación probabilística de planos (A-Roll vs B-Roll), corte dinámico y entrega multilingüe.
- **Jump Cut Engine:** Detección de silencios, preservación de pausas fonéticas naturales, micro-crossfades acústicos y saltos de escala (*punch-ins*) alternados para mantener el dinamismo visual.
- **Travel & Location Overlays:** Generadores procedurales de gráficos de viaje (GeoBadge, LocationCard, Polaroid con física de resorte amortiguado, cálculo de trayectorias geodésicas mediante fórmula de Haversine).
- **Voz Multilingüe Offline:** Soporte para 7 idiomas oficiales (es-MX, en-US, pt-BR, fr-FR, de-DE, it-IT, ja-JP) mediante Piper TTS local, con normalización textual de divisas, horas y porcentajes.
- **Interfaces Públicas:** Herramientas MCP especializadas (`vlog_generate_jump_cut_plan`, `vlog_classify_footage`, `vlog_match_broll`, `vlog_produce`, `vlog_get_status`), comando CLI `npm run vlog:produce` y directiva declarativa `vlog` en el DSL.

### Hito D: Motor Editorial Documental & Percepción Humana (v4.0.0)
- **Fase 4A — Perfiles Editoriales:** Configuración formal de tolerancias dramáticas, ratios de corte y estilos narrativos.
- **Fase 4B — Continuidad Visual & Acústica:** Auditoría automatizada de la regla de los 180°, coherencia de mirada (*eyeline match*), diferencias lumínicas y relleno de silencios mediante perfil de ruido de sala (*room tone*).
- **Fase 4C — Narrative Arc Engine:** Estructuración del metraje en 10 beats canónicos documentales (`HOOK`, `CONTEXT`, `QUESTION`, `EVIDENCE`, `TESTIMONY`, `CONFLICT`, `ESCALATION`, `REVELATION`, `RESOLUTION`, `REFLECTION`), grafo de causalidad temporal y blindaje contra revelaciones prematuras de datos (*anti-spoiler*).
- **Fase 4D — Fact & Evidence Verification:** Auditoría de afirmaciones (*claims*), vinculación con archivos probatorios, cálculo del índice de integridad factual (0–100) y generación automática de tarjetas de citación en pantalla.
- **Fase 4E — Archival Media & Universal Credits:** Movimiento suave 2D Ken Burns determinista para fotografías fijas, estampado de fechas históricas estandarizadas ("FILE FOOTAGE // YYYY"), auditoría de licencias y créditos finales estructurados.
- **Fase 4F — Trailer & Teaser Generator:** Síntesis promocional no destructiva en 4 formatos (15s Teaser, 30s Promo, 60s Trailer, 90s Epic) y evaluador predictivo de retención en los primeros 3 a 5 segundos (`SocialHookScorer`).
- **Fase 4G — Cinematic Match Cut Engine:** Detección de correspondencias formales entre planos adyacentes (geométrica, cromática, cinética, acústica) y cálculo del vector de compensación espacial $(\Delta X, \Delta Y)$ para transiciones fluidas invisibles.
- **Fase 4H — Psicología de la Atención & Carga Cognitiva:**
  - `AudienceAttentionModel`: Simulación diferencial $A(t)$ con baseline basal ($A_{\text{base}} = 0.40$), impulsos de novedad conmutativos y alertas de desinterés.
  - `CognitiveLoadEngine`: Índice de saturación sensorial multimodal $C(t) = 0.30V + 0.25D + 0.20S + 0.15M + 0.10K$ y mitigaciones no destructivas (*proposal-first*).
  - `EditorialContrast`: Control de rachas monótonas (`TensionRun`) y alternancia de energía dramática.
  - `PacingCurveComposer`: Alineación de la densidad de cortes contra la curva objetivo del perfil mediante distancia matemática $L_1$.

---

## 5. ¿Qué Cosas Faltan? (Las Próximas Fronteras)

A pesar de que el motor cuenta con una solidez técnica extraordinaria (Nivel 5 de Certificación y 1,004 pruebas), existen componentes de alto valor definidos en la especificación maestra [`spec/MASTER-CONTENT-ENGINE-v4.md`](file:///d:/Proyectos/TEST/AEREBUILD/spec/MASTER-CONTENT-ENGINE-v4.md) que aún no han sido implementados.

A continuación se detalla cada módulo faltante, ordenado por su impacto práctico en la producción:

---

### 🔍 Prioridad 1: Fase 4I — Editorial QA Linter, Human-in-the-Loop Governance & Semantic Diff Engine (REQ-030, REQ-081, REQ-082, REQ-083)
*Gobernanza transversal, agregación de diagnósticos, revisión asistida y medición de impacto $\Delta IR$.*

- **Principio Clave:** El linter **no recalcula nada**. Agrega diagnósticos emitidos por los motores especializados (`Attention`, `CognitiveLoad`, `Contrast`, `Pacing`, `Evidence`, `Continuity`, `MatchCut`, `Archival`, `Credits`) y aplica políticas de producción unificadas.
- **Contrato Transversal (`EditorialDiagnostic`):**
  - Unifica `BLOCKING`, `WARNING` y `SUGGESTION` con `ruleId`, `sourceEngine`, `confidence`, `suggestedFix` y `deterministicFingerprint`.
  - Los errores `BLOCKING` (ej. `LICENSE_MISSING`, `UNSUPPORTED_CLAIM`) jamás se ignoran por confianza.
- **`HumanReviewQueue` Calibrada:**
  - Políticas de revisión por tipo de regla (`confidencePolicyByRule`), enviando a revisión humana casos de incertidumbre sin frenar ediciones deterministas.
- **`EditorialDiffEngine` Semántico:**
  - Modela $\Delta IR = IR_{\text{before}} \to IR_{\text{after}}$ evaluando el impacto multidimensional: $\Delta\text{duración}$, $\Delta\text{pacing}$, $\Delta\text{atención}$, $\Delta\text{carga cognitiva}$, $\Delta\text{evidencias}$ y $\Delta\text{continuidad}$.

---

### 🌐 Prioridad 2: Fase 4J — Universal Timeline Exporters (OTIO, FCPXML, CMX EDL) (REQ-036)
*Interoperabilidad con toda la industria audiovisual más allá de After Effects.*

- **Arquitectura Unificada:** En lugar de construir exportadores divergentes, se introduce la capa intermedia:
  $$IR \to \text{TimelineExportModel} \to \{\text{AE JSX}, \text{OTIO}, \text{FCPXML}, \text{CMX EDL}\}$$
- Garantiza matemáticamente que `AE duration === OTIO duration === FCPXML clip offset`.

---

### 📊 Prioridad 3: Fase 4K — Data Visualization Engine (REQ-025)
*Gráficos estadísticos animados para periodismo de investigación y ensayos en vídeo.*

- **Sinergia con Fase 4D:** $\text{EvidenceEngine} \to \text{Dato Verificado} \to \text{DataVisualizationEngine} \to \text{AnimatedChart} \to \text{CognitiveLoadEngine} \to \text{Pacing} \to \text{QA}$.
- **Generadores:** `AnimatedBarChartCompiler`, `TrendLineGraphCompiler`, `BigStatCardGenerator` (TIME Style) y `ChronologyTimelineGenerator`.

---

### 🎥 Prioridad 4: Fase 4L — Multi-Camera Coverage & Synchronizer Engine (REQ-021 a REQ-024)
*Automatización completa de podcasts con vídeo, entrevistas y mesas redondas.*

- Sincronización precisa por timecode SMPTE y waveform acústico.
- Conmutación inteligente entre plano general, orador activo y planos de reacción del oyente.

---

### 🧠 Prioridad 5: Fase 5 (v4.1) — Scene Intelligence & Semantic Trimming Engine (REQ-042 a REQ-055)
*El gran salto ontológico hacia la estructura de escena y la preservación de la naturalidad humana.*

- **Reconstrucción Espacio-Temporal:** Agrupación semántica de clips en Escenas, ranking de relevancia multidimensional y ontologías temporales (presente vs flashback vs archivo vs recreación).
- **Poda Quirúrgica Semántica:** Supresión de redundancias conceptuales entre narrador y entrevistados, selector de mejor toma (*best take*) y preservación de vacilaciones reflexivas y calidez humana natural.

---

## 6. Nuevo Indicador Maestro: Editorial Decision Reliability (EDR)

A partir de la versión v4.0.0, el progreso del motor se evalúa mediante la confiabilidad editorial auditada:

| Métrica EDR | Definición / Fórmula | Objetivo de Producción |
| :--- | :--- | :--- |
| **Auditabilidad Criptográfica** | % de decisiones con `deterministicFingerprint` rastreable | **100.0%** |
| **Cobertura Temporal de QA** | % del timeline evaluado por diagnósticos multimodales | **100.0%** |
| **Defectos Críticos Escapados** | Número de issues `BLOCKING` no interceptados antes del render | **0** |
| **Tasa de Revisión Humana** | % de decisiones dudosas sometidas a `HumanReviewQueue` | Calibrado por regla |
| **Trazabilidad de Impacto** | % de modificaciones con vector $\Delta IR$ multidimensional cuantificado | **100.0%** |
| **Coherencia Multi-Exportador** | Discrepancia temporal entre AE JSX, OTIO y FCPXML | $\mathbf{0.0\text{ frames}}$ |

---

## 7. Guía de Inicio Rápido para Nuevos Agentes o Desarrolladores

### Comandos de Verificación y Compilación
```bash
# 1. Compilar código TypeScript a JavaScript estricto
npm run build

# 2. Ejecutar la batería completa de 1,004 pruebas unitarias, de integración y PBT
npm test

# 3. Ejecutar la suite de conformidad y re-emitir el certificado Nivel 5
npm run conformance

# 4. Producir un vlog de prueba mediante el CLI autónomo
npm run vlog:produce -- --dry-run --languages="es-MX,en-US"

# 5. Generar un micro-clip vertical de 1-clic con auto-reframe
npm run auto-clip
```

### Reglas Esenciales de Contribución
1. **Nunca modifiques tests existentes para disfrazar fallos.** Si una prueba falla, revisa la matemática y la implementación en `src/`.
2. **Todo módulo nuevo debe tener pruebas de 7 capas:** incluyendo al menos un test generativo con `fast-check` (Property-Based Test) que demuestre que las salidas están acotadas matemáticamente.
3. **Toda mejora debe registrarse en [`docs/POST_PHASE_IMPROVEMENTS.md`](file:///d:/Proyectos/TEST/AEREBUILD/docs/POST_PHASE_IMPROVEMENTS.md)** con el formato estandarizado (Fecha, Módulos, ¿Por qué?, ¿Para qué?, Archivos y Resultados de Pruebas).
4. **Sigue la Guía Visual:** Consulta [`docs/USER_DESIGN_PREFERENCES.md`](file:///d:/Proyectos/TEST/AEREBUILD/docs/USER_DESIGN_PREFERENCES.md) antes de proponer estilos tipográficos, paletas cromáticas o duraciones de plano.
