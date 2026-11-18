# Vlog Multilingual Production Orchestrator

**Archivo:** `20-VLOG-MULTILINGUAL-PRODUCTION-ORCHESTRATOR.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  
**Objetivo:** Orquestación completa y determinista de producción Vlog/Documental multilingüe  
**Dependencias:** Documentos 1–19  

---

## 1. Objetivo

Definir el sistema central que coordina toda la producción automática de un Vlog o Documental multilingüe.

El Orchestrator será responsable de convertir:
$$\text{Video crudo} + \text{Audio} + \text{B-Roll} + \text{Metadata} + \text{Configuración}$$
en:
$$\text{Proyecto multilingüe} + \text{Timelines} + \text{Audio Tracks} + \text{Subtítulos} + \text{B-Roll} + \text{Overlays} + \text{SFX} + \text{After Effects JSX} + \text{Reporte de Validación}$$

---

## 2. Regla Fundamental

El Orchestrator no implementará lógica audiovisual especializada. No deberá:
- transcribir directamente;
- clasificar frames;
- generar TTS;
- calcular overlays;
- realizar color grading;
- implementar subtítulos;
- generar SFX;
- manipular directamente After Effects.

Su función exclusiva será orquestar y coordinar módulos especializados mediante contratos formales.

---

## 3. Arquitectura

```
                    ┌───────────────────────┐
                    │ RAW PROJECT INPUT     │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ PROJECT VALIDATOR     │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ MEDIA INGESTION       │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ FOOTAGE CLASSIFIER    │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ TRANSCRIPTION         │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ NARRATIVE ANALYSIS    │
                    └───────────┬───────────┘
                                ↓
               ┌────────────────┴────────────────┐
               ↓                                 ↓
       ┌───────────────┐                ┌────────────────┐
       │ A-ROLL EDITOR │                │ B-ROLL MATCHER │
       └───────┬───────┘                └───────┬────────┘
               └────────────────┬───────────────┘
                                ↓
                    ┌───────────────────────┐
                    │ SOURCE TIMELINE      │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ LANGUAGE PLANNER      │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ TTS GENERATION        │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ ADAPTIVE PACING       │
                    └───────────┬───────────┘
                                ↓
               ┌────────────────┴────────────────┐
               ↓                                 ↓
       ┌───────────────┐                ┌────────────────┐
       │ SUBTITLE GEN  │                │ TRAVEL OVERLAY │
       └───────┬───────┘                └───────┬────────┘
               └────────────────┬───────────────┘
                                ↓
                    ┌───────────────────────┐
                    │ AUDIO MIX            │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ STYLE / COLOR        │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ AE JSX EXPORT        │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ VALIDATION            │
                    └───────────┬───────────┘
                                ↓
                    ┌───────────────────────┐
                    │ FINAL PACKAGE        │
                    └───────────────────────┘
```

---

## 4. Production Pipeline

Fases ordenadas de ejecución:
- `P00 INITIALIZE`
- `P01 VALIDATE_INPUT`
- `P02 INGEST_MEDIA`
- `P03 ANALYZE_MEDIA`
- `P04 CLASSIFY_FOOTAGE`
- `P05 TRANSCRIBE`
- `P06 ANALYZE_NARRATIVE`
- `P07 BUILD_SOURCE_TIMELINE`
- `P08 GENERATE_JUMP_CUTS`
- `P09 MATCH_BROLL`
- `P10 PLAN_LANGUAGES`
- `P11 GENERATE_TTS`
- `P12 ADAPTIVE_PACING`
- `P13 BUILD_SUBTITLES`
- `P14 BUILD_TRAVEL_OVERLAYS`
- `P15 BUILD_STYLE`
- `P16 BUILD_AUDIO`
- `P17 BUILD_TIMELINES`
- `P18 EXPORT_AE`
- `P19 VALIDATE_OUTPUT`
- `P20 PACKAGE_OUTPUT`
- `P21 COMPLETE`

---

## 5. Estados

```typescript
type ProductionState =
  | "PENDING"
  | "RUNNING"
  | "COMPLETED"
  | "FAILED"
  | "CANCELLED"
  | "BLOCKED"
  | "SKIPPED";
```

---

## 6. Estado Global

```typescript
interface ProductionRun {
  runId: string;
  projectId: string;
  state: ProductionState;
  currentPhase: ProductionPhase;
  startedAt: number;
  completedAt?: number;
  configurationHash: string;
  inputHash: string;
  phases: PhaseExecution[];
  warnings: ProductionWarning[];
  errors: ProductionError[];
}
```

---

## 7. Phase Execution

```typescript
interface PhaseExecution {
  phase: ProductionPhase;
  state: ProductionState;
  startedAt?: number;
  completedAt?: number;
  inputHash?: string;
  outputHash?: string;
  attempts: number;
  warnings: ProductionWarning[];
  errors: ProductionError[];
}
```

---

## 8. Phase Contract

```typescript
interface ProductionPhaseHandler<I, O> {
  readonly phase: ProductionPhase;
  validate(input: I): ValidationResult;
  execute(input: I, context: ProductionContext): Promise<O>;
  hashInput(input: I): string;
  hashOutput(output: O): string;
}
```

---

## 9. Production Context

```typescript
interface ProductionContext {
  projectId: string;
  runId: string;
  configuration: ProductionConfiguration;
  cache: ProductionCache;
  logger: ProductionLogger;
  artifactStore: ArtifactStore;
  eventBus: ProductionEventBus;
}
```

---

## 10. Production Configuration

```typescript
interface ProductionConfiguration {
  sourceLanguage: LanguageCode;
  targetLanguages: LanguageCode[];
  aspectRatios: AspectRatio[];
  stylePreset: string;
  outputDirectory: string;
  offlineMode: boolean;
  enableTTS: boolean;
  enableSubtitles: boolean;
  enableTravelOverlays: boolean;
  enableBrollMatching: boolean;
  enableJumpCuts: boolean;
  enableSocialPackage: boolean;
}
```

---

## 11. Default Offline Policy

$$\text{offlineMode} = \text{true} \quad (\text{cero APIs remotas obligatorias})$$

---

## 12. API Policy

Prohibidas dependencias accidentales de Internet. Cualquier servicio externo indispensable debe declararse como `EXTERNAL_DEPENDENCY_REQUIRED`.

---

## 13. Input Manifest

```typescript
interface ProjectManifest {
  projectId: string;
  media: MediaInput[];
  sourceLanguage: LanguageCode;
  targetLanguages: LanguageCode[];
  metadata?: ProjectMetadata;
  configuration: ProductionConfiguration;
}
```

---

## 14. Media Input

```typescript
interface MediaInput {
  id: string;
  path: string;
  type: MediaType;
  duration?: number;
  checksum?: string;
  metadata?: MediaMetadata;
}
```

---

## 15. Media Types

```typescript
type MediaType =
  | "VIDEO"
  | "AUDIO"
  | "IMAGE"
  | "DOCUMENT"
  | "UNKNOWN";
```

---

## 16. Input Validation

Validación previa de accesibilidad de rutas, formatos soportados, idiomas declarados y sintaxis de configuración.

---

## 17. Validation Failure

Fallo en validación obligatoria culmina en `P01 = FAILED` y `production = BLOCKED`.

---

## 18. Media Ingestion

P02 registra archivos, calcula hashes criptográficos y detecta FPS, resolución, codecs y canales de audio.

---

## 19. Media Fingerprint

```typescript
interface MediaFingerprint {
  checksum: string;
  size: number;
  duration?: number;
  width?: number;
  height?: number;
  fps?: number;
}
```

---

## 20. Duplicate Media

Detección de duplicados mediante coincidencia de checksums sin duplicación de procesamiento.

---

## 21. Media Cache

Archivos con huella idéntica reutilizan análisis previos sin re-procesar.

---

## 22. Analyze Media

P03 extrae presencia de audio, voz, flujo de movimiento, cambios de plano, iluminación y rostros.

---

## 23. Footage Classification

P04 invoca al `VlogFootageClassifier`.

---

## 24. Classification Output

```typescript
interface FootageClassification {
  mediaId: string;
  category:
    | "A_ROLL"
    | "B_ROLL"
    | "TIMELAPSE"
    | "ACTION"
    | "UNKNOWN";
  confidence: number;
  tags: string[];
}
```

---

## 25. Classification Confidence

$$\text{confidence} \in [0.0, 1.0]$$

---

## 26. Low Confidence

Confianzas bajo el umbral clasifican el archivo como `UNKNOWN` emitiendo advertencia.

---

## 27. Transcription

P05 utiliza `LocalWhisperTranscriptionBridge`.

---

## 28. Transcription Contract

```typescript
interface Transcript {
  language: LanguageCode;
  segments: TranscriptSegment[];
  duration: number;
  confidence: number;
}
```

---

## 29. Transcript Segment

```typescript
interface TranscriptSegment {
  id: string;
  start: number;
  end: number;
  text: string;
  words: TranscriptWord[];
}
```

---

## 30. Word Timing

```typescript
interface TranscriptWord {
  word: string;
  start: number;
  end: number;
  confidence: number;
}
```

---

## 31. Transcription Failure

Fallo en Whisper emite `TRANSCRIPTION_FAILED` y detiene el flujo si la transcripción es crítica.

---

## 32. Narrative Analysis

P06 extrae hooks, oraciones, entidades, giros temáticos, pausas y beats dramáticos.

---

## 33. Narrative Segment

```typescript
interface NarrativeSegment {
  id: string;
  start: number;
  end: number;
  text: string;
  topic?: string;
  entities: NarrativeEntity[];
  emphasis: EmphasisLevel;
  beat: NarrativeBeat;
}
```

---

## 34. Narrative Beats

```typescript
type NarrativeBeat =
  | "HOOK"
  | "SETUP"
  | "CONTEXT"
  | "DEVELOPMENT"
  | "CLIMAX"
  | "REFLECTION"
  | "CTA"
  | "OUTRO";
```

---

## 35. Source Timeline

P07 construye la línea temporal base en el idioma original como referencia narrativa maestra.

---

## 36. Source Timeline Invariant

Preservación inmutable del orden narrativo y referencias semánticas de origen.

---

## 37. Jump Cut Phase

P08 invoca a `VlogJumpCutEngine`.

---

## 38. Jump Cut Contract

Generación de línea temporal depurada, eventos de corte, regiones silenciadas y candidatos de punch-in.

---

## 39. Silence Removal

$$\text{silenceRemoveThreshold} = 0.25\text{ s} \quad (\text{por defecto})$$

---

## 40. Micro Crossfade

$$\text{crossfadeDuration} = 10\text{ ms} \quad (0.010\text{ s})$$

---

## 41. Punch-In

$$\text{punchInScale} = 100\% \longrightarrow 115\% \longrightarrow 100\%$$

---

## 42. Punch-In Trigger

Activación por énfasis vocal, cambio temático o clímax narrativo.

---

## 43. B-Roll Matching

P09 invoca al emparejador semántico `BRollMatcher`.

---

## 44. B-Roll Match Input

```typescript
interface BrollMatchInput {
  narrativeSegment: NarrativeSegment;
  availableClips: ClassifiedClip[];
  targetDuration: number;
}
```

---

## 45. B-Roll Match Score

Ponderación de relevancia semántica, calidad visual, duración útil y frescura temporal.

---

## 46. Match Score

$$\text{score} \in [0, 100]$$

---

## 47. Duplicate B-Roll

Penalización incremental por reutilización consecutiva o cercana del mismo clip.

---

## 48. B-Roll Confidence

Sin candidatos que superen `minimumMatchScore`, se mantiene A-Roll limpio en lugar de B-Roll forzado.

---

## 49. Language Planning

P10 define locales, voces seleccionadas, tasas de lectura y modos de subtitulado.

---

## 50. Language Matrix

Matriz de capacidades por idioma (`es-MX`, `en-US`, `pt-BR`, `fr-FR`, `de-DE`).

---

## 51. TTS Generation

P11 invoca al `MultilingualVoiceoverEngine`.

---

## 52. TTS Contract

```typescript
interface VoiceoverTrack {
  language: LanguageCode;
  voiceId: string;
  audioPath: string;
  duration: number;
  segments: VoiceoverSegment[];
  checksum: string;
}
```

---

## 53. Voiceover Segment

```typescript
interface VoiceoverSegment {
  narrativeSegmentId: string;
  start: number;
  end: number;
  text: string;
}
```

---

## 54. TTS Offline Requirement

Voces locales prioritarias; prohibida dependencia obligatoria de APIs de pago.

---

## 55. TTS Failure

El fallo en un idioma individual no invalida las pistas de los demás idiomas.

---

## 56. Partial Language Failure

Continuación permitida si `allowPartialLanguages: true`.

---

## 57. Adaptive Pacing

P12 invoca al `VlogAdaptivePacingEngine`.

---

## 58. Pacing Inputs

Línea temporal fuente, duraciones de locución, clips de B-Roll y segmentos narrativos.

---

## 59. Pacing Objective

Minimizar desincronizaciones visuales y estiramientos forzados de voz.

---

## 60. Voice Time Stretch

Rango permitido por defecto: $[0.95\text{x}, 1.05\text{x}]$.

---

## 61. Stretch Policy

$$\text{Ajustar B-Roll} \longrightarrow \text{Ajustar pausas} \longrightarrow \text{Transiciones} \longrightarrow \text{Micro stretch vocal} \longrightarrow \text{Reporte de conflicto}$$

---

## 62. Forbidden Stretch

Prohibido rebasar $[0.95\text{x}, 1.05\text{x}]$ sin instrucción explícita.

---

## 63. Segment Alignment

Mapeo determinista de cada segmento vocal hacia sus correspondientes eventos visuales.

---

## 64. Alignment Contract

```typescript
interface SegmentAlignment {
  narrativeSegmentId: string;
  voiceStart: number;
  voiceEnd: number;
  visualStart: number;
  visualEnd: number;
  offset: number;
}
```

---

## 65. Maximum Drift

$$\text{maxDrift} = 100\text{ ms}$$

---

## 66. Drift Failure

Desviaciones superiores a $100\text{ ms}$ emiten advertencia o fallo crítico según la importancia del segmento.

---

## 67. Subtitle Generation

P13 utiliza `Typography Engine` y los timestamps palabra por palabra del audio activo.

---

## 68. Subtitle Source

Transcripción fuente para idioma original y guiones sintetizados para versiones TTS.

---

## 69. Subtitle Timing

Sincronía estricta de subtítulos con la locución de cada idioma derivado.

---

## 70. Subtitle Modes

`STANDARD`, `WORD_BY_WORD`, `KARAOKE`, `EMPHASIS`.

---

## 71. Subtitle Safety

Respeto riguroso de zonas seguras y prevención de colisión con rostros.

---

## 72. Travel Overlays

P14 invoca al `VlogTravelOverlays`.

---

## 73. Overlay Sources

Metadatos GPS, etiquetas narrativas, números de capítulo e información de producción.

---

## 74. Overlay Localization

Rótulos y badges traducidos dinámicamente según el locale de entrega.

---

## 75. Style

P15 aplica el preset visual seleccionado (`TIME`, `Cinematic Travel`, etc.).

---

## 76. Style Inheritance

$$\text{Global Style} \longrightarrow \text{Project Style} \longrightarrow \text{Language Override} \longrightarrow \text{Scene Override} \longrightarrow \text{Element Override}$$

---

## 77. Audio

P16 mezcla voz, música de fondo, efectos SFX y sonido ambiente.

---

## 78. Audio Priority

$$\text{VOICE} > \text{CRITICAL SFX} > \text{MUSIC} > \text{AMBIENCE}$$

---

## 79. Ducking

Atenuación automática de la música ante la presencia de diálogo.

---

## 80. Audio Output

Generación de master de audio independiente por cada idioma (`master_es.wav`, `master_en.wav`, etc.).

---

## 81. Timeline Generation

P17 instancia una línea temporal independiente por idioma.

---

## 82. Timeline IDs

$$\text{timeline\_<projectId>\_<language>}$$

---

## 83. Language Isolation

Modificaciones sobre `en-US` no alteran los timelines de `es-MX`, `pt-BR`, `fr-FR` o `de-DE`.

---

## 84. Shared Assets

Reutilización compartida de clips de video, fotografías, mapas y efectos de sonido.

---

## 85. Language-Specific Assets

Aislamiento de audios vocales, subtítulos y textos gráficos localizados.

---

## 86. After Effects Export

P18 genera los scripts JSX finales de composición.

---

## 87. JSX Package

Emisión de archivos JSX modulares (`project_es.jsx`, `project_en.jsx`, etc.).

---

## 88. JSX Determinism

Misma entrada genera idéntico árbol de código JSX reproducible.

---

## 89. AE Compatibility

Compatibilidad nativa con After Effects en inglés y en español mediante Universal Match Names.

---

## 90. Validation

P19 ejecuta auditoría de 7 capas sobre el proyecto ensamblado.

---

## 91. Validation Layers

Esquemas, medios, timelines, audio, textos, localización, layout, safe zones, overlays, JSX y determinismo.

---

## 92. Validation Result

```typescript
interface ProductionValidation {
  valid: boolean;
  blockingErrors: ValidationError[];
  warnings: ProductionWarning[];
  metrics: ValidationMetrics;
}
```

---

## 93. Blocking Errors

Archivos de audio ausentes, colisiones fatales o errores de exportación JSX impiden la entrega.

---

## 94. Warnings

Confianzas bajas de B-roll o fuentes sustituidas se reportan como advertencias sin bloquear.

---

## 95. Quality Gate

Prohibido marcar una producción como `COMPLETED` si persisten errores bloqueantes.

---

## 96. Package Output

P20 estructura la carpeta de entrega final:
```
output/
├── project/
├── audio/
├── subtitles/
├── jsx/
├── overlays/
├── metadata/
├── reports/
└── manifests/
```

---

## 97. Language Directory

Subdirectorios aislados por idioma: `es-MX/`, `en-US/`, `pt-BR/`, `fr-FR/`, `de-DE/`.

---

## 98. Language Package

Cada paquete de idioma contiene su propio audio master, subtítulos SRT/JSON, timeline y JSX.

---

## 99. Manifest Final

```typescript
interface FinalManifest {
  projectId: string;
  runId: string;
  languages: LanguagePackage[];
  sourceAssets: string[];
  sharedAssets: string[];
  configurationHash: string;
  productionHash: string;
  validation: ProductionValidation;
}
```

---

## 100. Atomic Output

Prohibido escribir directamente sobre la carpeta final de entrega durante el procesamiento.

---

## 101. Temporary Workspace

Toda fase opera dentro del espacio de trabajo temporal `work/<runId>/`.

---

## 102. Commit

El traslado atómico $\text{work/<runId>} \to \text{output/}$ ocurre únicamente tras superar la validación P19.

---

## 103. Atomic Commit Failure

Fallo en el commit marca `production = FAILED` preservando intactos los entregables anteriores.

---

## 104. Idempotency

$$\text{run}(\text{input}) \equiv \text{run}(\text{input}) \quad (\text{idéntico resultado lógico})$$

---

## 105. Idempotency Key

$$\text{idempotencyKey} = \text{SHA-256}(\text{inputHash} + \text{configurationHash} + \text{engineVersion})$$

---

## 106. Cache Reuse

Coincidencia de clave reutiliza directamente los artefactos cacheados.

---

## 107. Cache Invalidation

Cambios en entradas, versiones de motor o configuración invalidan la caché respectiva.

---

## 108. Phase Retry

Reintento automático ante fallos recuperables.

---

## 109. Retry Policy

$$\text{maxAttempts} = 3$$

---

## 110. Non-Retryable Errors

Errores de sintaxis de configuración, schemas o archivos faltantes no se reintentan.

---

## 111. Retryable Errors

Interrupciones transitorias de procesos, timeouts o bloqueos momentáneos de disco son reintentables.

---

## 112. Timeout

Límite de tiempo máximo configurable por fase (`timeoutMs`).

---

## 113. Timeout Failure

Superar el timeout cancela el proceso worker y marca la fase como `FAILED`.

---

## 114. Cancellation

Soporte de cancelación limpia solicitada por el usuario.

---

## 115. Cancellation Behavior

Interrupción de workers activos, purga de temporales y preservación de artefactos previos consolidados.

---

## 116. Resume

Reanudación inteligente de producciones incompletas desde la última fase válida.

---

## 117. Resume Validation

Verificación previa de coincidencia de hashes de entrada y versión antes de reanudar.

---

## 118. Corrupted Artifact

Artefactos cacheados con hash corrupto se invalidan y fuerzan el re-procesamiento de la fase.

---

## 119. Event Bus

```typescript
type ProductionEvent =
  | "RUN_STARTED"
  | "PHASE_STARTED"
  | "PHASE_COMPLETED"
  | "PHASE_FAILED"
  | "WARNING"
  | "ARTIFACT_CREATED"
  | "RUN_CANCELLED"
  | "RUN_COMPLETED";
```

---

## 120. Event Payload

```typescript
interface ProductionEventPayload {
  runId: string;
  projectId: string;
  phase?: ProductionPhase;
  timestamp: number;
  metadata?: Record<string, unknown>;
}
```

---

## 121. Logging

Registro estructurado de inicio, fin, hashes, consumo de memoria y advertencias.

---

## 122. Log Levels

`DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`.

---

## 123. Structured Logs

Emisión en formato JSON Lines para indexación.

---

## 124. No Secrets

Prohibida la inclusión de contraseñas, tokens o claves en los registros.

---

## 125. Resource Management

Límites de concurrencia de CPU, RAM máxima y procesos paralelos según configuración.

---

## 126. Parallelization

Ejecución concurrente de tareas independientes (ej. síntesis TTS simultánea de los 5 idiomas).

---

## 127. Parallelization Constraint

Fases con dependencia directa nunca se ejecutan en paralelo.

---

## 128. Dependency Graph

Grafo Acíclico Dirigido (DAG) de dependencias estrictas entre fases P01 a P21.

---

## 129. Language Worker Isolation

Aislamiento de cada idioma en un contexto de ejecución lógico independiente.

---

## 130. Worker Failure

El fallo en el worker de un idioma no cancela los demás trabajadores si la política lo permite.

---

## 131. Production Completion Policy

```typescript
completionPolicy:
  | "ALL_LANGUAGES_REQUIRED"
  | "ALLOW_PARTIAL_LANGUAGES";
```

---

## 132. ALL_LANGUAGES_REQUIRED

Un solo idioma fallido detiene la producción y la marca como `FAILED`.

---

## 133. ALLOW_PARTIAL_LANGUAGES

Los idiomas finalizados con éxito se empaquetan marcando `partial: true`.

---

## 134. Source Language Priority

El idioma original se procesa y consolida con prioridad conceptual.

---

## 135. Source Timeline Authority

La línea temporal base es la autoridad narrativa indiscutible.

---

## 136. Semantic Invariant

Todos los idiomas derivados conservan la secuencia de capítulos, orden de ideas y llamadas a la acción.

---

## 137. Language Extensibility

Incorporar un nuevo idioma (`it-IT`) no requiere modificar el núcleo del Orchestrator.

---

## 138. Plugin Architecture

Registro dinámico de controladores de fase mediante `PhaseRegistry`.

---

## 139. Phase Registry

```typescript
interface PhaseRegistry {
  register<I, O>(phase: ProductionPhase, handler: ProductionPhaseHandler<I, O>): void;
  get(phase: ProductionPhase): ProductionPhaseHandler<any, any>;
}
```

---

## 140. Unknown Phase

Fase requerida no registrada emite `PHASE_NOT_REGISTERED` y bloquea la producción.

---

## 141. Configuration Schema

Validación estricta de esquemas de configuración de producción.

---

## 142. Configuration Version

Inclusión obligatoria de `schemaVersion: "1.0.0"`.

---

## 143. Backward Compatibility

Migración transparente de configuraciones antiguas mediante `ConfigurationMigrator`.

---

## 144. Migration

Las migraciones generan configuraciones normalizadas sin alterar los archivos de entrada.

---

## 145. Dry Run

Modo `--dry-run` para verificación integral sin generación de entregables en disco.

---

## 146. Dry Run Behavior

Audita dependencias, sintaxis, espacio en disco y permisos de archivos.

---

## 147. Preview Mode

Modo `--preview` para generación acotada de un fragmento de prueba.

---

## 148. Preview Range

Parámetros delimitadores: `--start 0 --duration 30`.

---

## 149. Preview Purpose

Validación rápida de ritmo, entonación y estilo sin procesar horas de metraje.

---

## 150. Production CLI

Comando oficial: `npm run vlog:produce`.

---

## 151. CLI Input

```bash
npm run vlog:produce -- --manifest project.json --languages es-MX,en-US,pt-BR --style cinematic-travel
```

---

## 152. CLI Resume

```bash
npm run vlog:produce -- --resume <runId>
```

---

## 153. CLI Validate

```bash
npm run vlog:produce -- --validate-only --manifest project.json
```

---

## 154. CLI Dry Run

```bash
npm run vlog:produce -- --dry-run --manifest project.json
```

---

## 155. MCP Integration

Herramienta MCP `create_vlog_production`.

---

## 156. MCP Request

```typescript
interface CreateVlogProductionRequest {
  manifest: ProjectManifest;
  options?: ProductionOptions;
}
```

---

## 157. MCP Response

```typescript
interface CreateVlogProductionResponse {
  runId: string;
  state: ProductionState;
  phases: PhaseExecution[];
}
```

---

## 158. MCP Status

Herramienta `get_vlog_production_status`.

---

## 159. MCP Cancel

Herramienta `cancel_vlog_production`.

---

## 160. MCP Resume

Herramienta `resume_vlog_production`.

---

## 161. MCP Logs

Herramienta `get_vlog_production_logs`.

---

## 162. Artifact Store

Persistencia estructurada de artefactos intermedios por fase (`artifacts/voiceover/`, etc.).

---

## 163. Artifact Metadata

```typescript
interface ArtifactMetadata {
  artifactId: string;
  type: string;
  phase: ProductionPhase;
  createdAt: number;
  checksum: string;
  engineVersion: string;
  dependencies: string[];
}
```

---

## 164. Artifact Immutability

Los artefactos completados son de solo lectura e inmutables.

---

## 165. Artifact Versioning

Cambios en las entradas generan nuevas revisiones de artefactos.

---

## 166. Dependency Tracking

Declaración explícita de artefactos consumidos para trazabilidad.

---

## 167. Dependency Graph Validation

Verificación de concordancia de hashes de dependencias antes de reutilizar caché.

---

## 168. Garbage Collection

Purga segura de artefactos obsoletos preservando las ejecuciones activas.

---

## 169. Disk Safety

Estimación previa del espacio en disco requerido antes de procesar tareas pesadas.

---

## 170. Insufficient Disk

Espacio insuficiente emite `INSUFFICIENT_DISK_SPACE` y bloquea la ejecución preventiva.

---

## 171. Crash Recovery

Detección automática de estados interrumpidos (`INTERRUPTED`) en arranques posteriores.

---

## 172. Recovery

Reanudación preservando los artefactos validados y repitiendo la fase inconclusa.

---

## 173. No Corrupted Final Project

Prohibido marcar el proyecto como concluido antes de la validación y commit atómico.

---

## 174. Production Hash

Hash unificado representativo de entradas, configuración, versiones y artefactos.

---

## 175. Reproducibility

Misma entrada, configuración y semilla genera idéntico resultado audiovisual final.

---

## 176. Floating Point

Respeto estricto de tolerancias matemáticas $\epsilon \le 10^{-10}$.

---

## 177. Time Precision

Tiempos continuos en precisión de punto flotante de 64 bits.

---

## 178. Frame Boundary

Cuantización a fotogramas enteros realizada exclusivamente en el exportador final.

---

## 179. Timeline Semantics

Semántica semidesierta $[t_{\text{start}}, t_{\text{end}})$ estandarizada.

---

## 180. No Hidden Timeline Offsets

Prohibida la introducción de offsets silenciosos no modelados como eventos.

---

## 181. Production Metrics

Registro de tiempos de procesamiento, consumo de recursos, aciertos de caché y conteos de cortes.

---

## 182. Efficiency Metric

$$\text{processingRatio} = \frac{\text{processingTime}}{\text{mediaDuration}}$$

---

## 183. Cache Efficiency

$$\text{cacheHitRate} = \frac{\text{cacheHits}}{\text{cacheHits} + \text{cacheMisses}}$$

---

## 184. Quality Metrics

Promedios de confianza en Whisper, alineación TTS, deriva de pacing y colisiones de overlays.

---

## 185. Final Report

Generación obligatoria de `production-report.json` y `production-report.md`.

---

## 186. Report Sections

Proyecto, medios, idiomas, rendimiento, audio, subtítulos, B-roll, overlays, validación y reproducibilidad.

---

## 187. Testing Strategy

Estrategia en 4 niveles: Unitario, Integración, Basado en Propiedades y End-to-End.

---

## 188. Unit Tests

Pruebas de registro de fases, orden de dependencias, hashing y políticas de reintento.

---

## 189. Integration Tests

Validación de interfaces de paso entre fases contiguas.

---

## 190. End-to-End Test

Fixture de prueba de 30–60 segundos con A-Roll, B-Roll, música, subtítulos y overlays.

---

## 191. Full Multilingual E2E

Prueba integral en los 5 idiomas oficiales (`es-MX`, `en-US`, `pt-BR`, `fr-FR`, `de-DE`).

---

## 192. Failure Injection Tests

Simulación de audios corruptos, fallos en Whisper, disco lleno y caídas de procesos.

---

## 193. Expected Failure Behavior

Aislamiento de la falla, preservación de artefactos previos y reporte estructurado sin corrupción final.

---

## 194. Cancellation Test

Verificación de consistencia del sistema ante cancelaciones en pleno render.

---

## 195. Resume Test

Comprobación de que la reanudación reutiliza los artefactos válidos previos.

---

## 196. Determinism Test

Comparación de hashes entre dos ejecuciones idénticas del mismo fixture.

---

## 197. Expected Determinism

Coincidencia exacta de hashes de timelines, overlays, subtítulos y JSX.

---

## 198. Language Isolation Test

Modificar la locución en inglés no altera los artefactos ni subtítulos en español.

---

## 199. Configuration Isolation Test

Cambiar estilos de texto no invalida los análisis de audio o transcripción.

---

## 200. Performance Test

Benchmarks de rendimiento sobre proyectos de 30, 60 y 120 minutos.

---

## 201. Memory Test

Procesamiento sin desbordamiento de RAM mediante liberación activa de buffers.

---

## 202. Streaming Requirement

Procesamiento por bloques para análisis acústico y de flujo visual.

---

## 203. Worker Isolation

Fallos en workers individuales no contaminan el estado global del orquestador.

---

## 204. Thread Safety

Almacenes y cachés seguros ante accesos concurrentes.

---

## 205. Locking

Bloqueo de lectura sobre artefactos en proceso de escritura.

---

## 206. Atomic Artifact Write

$$\text{Temporal} \longrightarrow \text{Checksum} \longrightarrow \text{fsync} \longrightarrow \text{Renombrado atómico}$$

---

## 207. Security

Validación de rutas para impedir fugas por Path Traversal.

---

## 208. Input Path Policy

Bloqueo de secuencias `../` fuera de directorios explícitamente autorizados.

---

## 209. Output Isolation

Salida restringida al directorio configurado por el usuario.

---

## 210. External Process Isolation

Wrappers controlados para invocaciones a herramientas nativas locales.

---

## 211. Process Arguments

Prohibida la concatenación de cadenas crudas sin sanitización previa.

---

## 212. Environment

Variables de entorno declaradas explícitamente sin herencias opacas.

---

## 213. Error Context

Inclusión de runId, fase, artefacto, medio e idioma en cada registro de error.

---

## 214. Error Format

```typescript
interface ProductionError {
  code: string;
  message: string;
  phase: ProductionPhase;
  retryable: boolean;
  blocking: boolean;
  context?: Record<string, unknown>;
}
```

---

## 215. Warning Format

```typescript
interface ProductionWarning {
  code: string;
  message: string;
  phase: ProductionPhase;
  context?: Record<string, unknown>;
}
```

---

## 216. Error Codes Mínimos

- `INVALID_MANIFEST`
- `INVALID_CONFIGURATION`
- `MEDIA_NOT_FOUND`
- `MEDIA_UNSUPPORTED`
- `MEDIA_CORRUPTED`
- `INSUFFICIENT_DISK_SPACE`
- `PHASE_NOT_REGISTERED`
- `PHASE_TIMEOUT`
- `PHASE_FAILED`
- `TRANSCRIPTION_FAILED`
- `NARRATIVE_ANALYSIS_FAILED`
- `BROLL_MATCH_FAILED`
- `TTS_FAILED`
- `PACING_FAILED`
- `SUBTITLE_FAILED`
- `OVERLAY_FAILED`
- `AUDIO_MIX_FAILED`
- `AE_EXPORT_FAILED`
- `VALIDATION_FAILED`
- `COMMIT_FAILED`
- `ARTIFACT_CORRUPTED`
- `RUN_CANCELLED`

---

## 217. State Machine

$$\text{PENDING} \longrightarrow \text{RUNNING} \longrightarrow \text{COMPLETED} \;|\; \text{FAILED} \;|\; \text{CANCELLED}$$

---

## 218. Invalid State Transitions

Transiciones regresivas (`COMPLETED` $\to$ `RUNNING`) prohibidas sin reintento formal.

---

## 219. Resume State

La reanudación genera un nuevo run lógico vinculado (`parentRunId`).

---

## 220. Run Lineage

```typescript
interface RunLineage {
  runId: string;
  parentRunId?: string;
  resumedFromPhase?: ProductionPhase;
}
```

---

## 221. Audit Trail

Trazabilidad completa: iniciador, configuración, versiones, transiciones y resultados.

---

## 222. Automation Entry Points

Invocable mediante CLI, herramientas MCP, API programática o schedulers.

---

## 223. Programmatic API

```typescript
interface VlogProductionService {
  create(manifest: ProjectManifest): Promise<ProductionRun>;
  status(runId: string): Promise<ProductionRun>;
  cancel(runId: string): Promise<void>;
  resume(runId: string): Promise<ProductionRun>;
}
```

---

## 224. No Direct Module Coupling

Comunicación entre módulos exclusivamente mediante interfaces y artefactos tipados.

---

## 225. Dependency Injection

El Orchestrator recibe todos los servicios especializados mediante inyección de dependencias.

---

## 226. Testability

Soporte nativo para servicios simulados (*mocks*) en suites de prueba unitarias.

---

## 227. No Hidden Singleton State

Prohibido el uso de variables globales mutables o estados compartidos ocultos.

---

## 228. Configuration Snapshot

Congelación de la configuración activa al inicio de la ejecución.

---

## 229. Engine Version Snapshot

Registro inmutable de la versión del motor (`engineVersion`).

---

## 230. Seed

Propagación de semilla determinista (`seed: number`) para variaciones visuales.

---

## 231. Seed Propagation

La semilla gobierna rotaciones Polaroid, desempates de B-roll y micro-variaciones.

---

## 232. No Seed From Clock

Prohibido utilizar el reloj del sistema como semilla implícita.

---

## 233. Time Source

Los timestamps operativos de logs usan tiempo real; los cálculos audiovisuales no dependen de él.

---

## 234. Final Completion Criteria

Una producción culmina en `COMPLETED` únicamente cuando todas las fases P01 a P21 resultan aprobadas (`PASS`).

---

## 235. Definition of Done

- [ ] Pipeline completo implementado
- [ ] DAG de dependencias
- [ ] PhaseRegistry
- [ ] ProductionContext
- [ ] ArtifactStore
- [ ] Cache
- [ ] Hashing
- [ ] Idempotencia
- [ ] Resume
- [ ] Retry
- [ ] Timeout
- [ ] Cancellation
- [ ] Crash recovery
- [ ] Atomic output commit
- [ ] Media ingestion
- [ ] Classification
- [ ] Whisper transcription
- [ ] Narrative analysis
- [ ] Source timeline
- [ ] Jump cuts
- [ ] B-roll matching
- [ ] Language planning
- [ ] Local TTS
- [ ] Adaptive pacing
- [ ] Multilingual subtitles
- [ ] Travel overlays
- [ ] Style application
- [ ] Audio mixing
- [ ] Timeline generation
- [ ] AE JSX export
- [ ] ES-MX, EN-US, PT-BR, FR-FR, DE-DE
- [ ] Offline mode
- [ ] Language isolation
- [ ] Determinism
- [ ] Seeded randomness
- [ ] Performance metrics
- [ ] Structured logs
- [ ] Validation reports
- [ ] CLI
- [ ] MCP create, status, cancel, resume, logs
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] Failure injection
- [ ] Cancellation tests
- [ ] Resume tests
- [ ] Determinism tests
- [ ] Language isolation tests
- [ ] Performance tests
- [ ] Security tests

---

## 236. Regla de Implementación

Este documento no autoriza todavía la implementación del Orchestrator. Primero deberán existir y estar validados los contratos de datos y módulos que consume:
$$\text{CONTRATOS} \longrightarrow \text{UNIT TESTS} \longrightarrow \text{IMPLEMENTACIÓN DE MÓDULOS} \longrightarrow \text{INTEGRACIÓN} \longrightarrow \text{ORCHESTRATOR} \longrightarrow \text{E2E}$$

---

## 237. Criterio de Integridad

El Orchestrator se considerará terminado únicamente si puede:
- Iniciar una producción desde un manifest.
- Validar todas las entradas.
- Ejecutar las fases en estricto orden.
- Paralelizar tareas independientes.
- Aislar idiomas derivados.
- Reutilizar artefactos cacheados.
- Recuperarse de interrupciones o caídas.
- Reintentar fallos transitorios.
- Cancelar limpiamente.
- Generar un paquete final atómico validado.
- Reproducir el mismo resultado con idéntica entrada y semilla.
- Operar de forma 100% offline.

---

## 238. Estado Final

**Documento:** `20-VLOG-MULTILINGUAL-PRODUCTION-ORCHESTRATOR.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  
**Dependencias críticas:** Documentos 1–19
