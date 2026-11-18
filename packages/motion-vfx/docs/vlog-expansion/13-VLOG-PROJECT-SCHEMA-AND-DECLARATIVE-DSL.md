# Vlog Project Schema & Declarative Production DSL

**Documento:** `13-VLOG-PROJECT-SCHEMA-AND-DECLARATIVE-DSL.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  

---

## 1. Objetivo

Definir el contrato maestro de datos utilizado por todo el pipeline Vlog/Documental.

Este documento establece:
- estructura del proyecto;
- schema;
- entidades;
- IDs;
- relaciones;
- clips;
- escenas;
- segmentos;
- A-Roll;
- B-Roll;
- voz;
- idiomas;
- subtítulos;
- música;
- SFX;
- overlays;
- mapas;
- localizaciones;
- presets;
- timeline;
- composición;
- variantes;
- validaciones;
- exportación;
- reproducibilidad;
- versionado.

El objetivo es que ningún módulo tenga que inferir o inventar información que debería estar explícitamente definida.

---

## 2. Fuente Única de Verdad

El proyecto deberá tener un único documento maestro: `vlog-project.json`. Todos los subsistemas deberán consumir este contrato:

```
vlog-project.json
        │
        ├── Ingestion
        ├── Transcription
        ├── Classification
        ├── Jump Cuts
        ├── Localization
        ├── Voiceover
        ├── Pacing
        ├── Music/SFX
        ├── Overlays
        ├── Reframing
        ├── Subtitles
        ├── AE Export
        └── Validation
```

---

## 3. Regla Fundamental

Ningún módulo deberá modificar silenciosamente la fuente original. El pipeline deberá utilizar:

$$\text{INPUT} \longrightarrow \text{DERIVED STATE} \longrightarrow \text{RESOLVED TIMELINE} \longrightarrow \text{OUTPUT}$$

---

## 4. Project ID

Todo proyecto deberá tener un ID único: `type ProjectId = string;` (ejemplo: `vlog_guadalajara_001`).

---

## 5. ID Rules

Los IDs deberán:
- ser únicos dentro del proyecto;
- ser estables;
- no depender del índice de un array;
- no cambiar por reordenamiento;
- no utilizar timestamps como única identidad.

---

## 6. ID Format

Formato recomendado:
$$\text{<entity-type>\_<human-readable-slug>\_<short-id>}$$
Ejemplos: `clip_market_7f21`, `scene_center_01`, `segment_intro_a91f`, `overlay_geo_003`.

---

## 7. Schema Version

Todo proyecto deberá declarar:
```json
{
  "schemaVersion": "1.0.0"
}
```

---

## 8. Engine Version

Deberá conservarse:
```json
{
  "engineVersion": "3.4.0"
}
```
La versión del schema y la versión del motor son independientes.

---

## 9. Project Root

```typescript
interface VlogProject {
  schemaVersion: string;
  engineVersion: string;
  projectId: ProjectId;
  metadata: ProjectMetadata;
  settings: ProjectSettings;
  assets: AssetRegistry;
  locations: LocationRegistry;
  clips: ClipRegistry;
  scenes: SceneRegistry;
  segments: SegmentRegistry;
  languages: LanguageRegistry;
  timelines: TimelineRegistry;
  audio: AudioProjectConfig;
  subtitles: SubtitleProjectConfig;
  overlays: OverlayProjectConfig;
  exports: ExportConfig;
}
```

---

## 10. Metadata

```typescript
interface ProjectMetadata {
  title: string;
  description?: string;
  creator?: string;
  createdAt?: string;
  source?: string;
  tags?: string[];
}
```
`createdAt` será informativo y no deberá alterar el resultado visual.

---

## 11. Project Settings

```typescript
interface ProjectSettings {
  defaultLocale: SupportedLocale;
  defaultAspectRatio: AspectRatio;
  defaultFrameRate: number;
  defaultResolution: Resolution;
  unitSystem: UnitSystem;
  deterministic: boolean;
}
```

---

## 12. Supported Locales

Mínimo: `es-MX`, `es-ES`, `en-US`, `en-GB`, `pt-BR`, `fr-FR`, `de-DE`. La arquitectura deberá permitir agregar idiomas posteriormente.

---

## 13. Aspect Ratios

```typescript
type AspectRatio =
  | "16:9"
  | "9:16"
  | "1:1"
  | "4:5"
  | "21:9";
```

---

## 14. Resolution

```typescript
interface Resolution {
  width: number;
  height: number;
}
```

---

## 15. Frame Rate

Deberán admitirse valores arbitrarios válidos: $23.976, 24, 25, 29.97, 30, 50, 59.94, 60$.

---

## 16. Asset Registry

```typescript
interface AssetRegistry {
  videos: VideoAsset[];
  audio: AudioAsset[];
  images: ImageAsset[];
  fonts: FontAsset[];
  maps: MapAsset[];
  graphics: GraphicAsset[];
}
```

---

## 17. Asset Base

```typescript
interface BaseAsset {
  id: string;
  path: string;
  hash?: string;
  duration?: number;
  metadata?: Record<string, unknown>;
}
```

---

## 18. Video Asset

```typescript
interface VideoAsset extends BaseAsset {
  type: "VIDEO";
  width: number;
  height: number;
  fps: number;
  duration: number;
  hasAudio: boolean;
}
```

---

## 19. Audio Asset

```typescript
interface AudioAsset extends BaseAsset {
  type: "AUDIO";
  duration: number;
  sampleRate: number;
  channels: number;
}
```

---

## 20. Image Asset

```typescript
interface ImageAsset extends BaseAsset {
  type: "IMAGE";
  width: number;
  height: number;
}
```

---

## 21. Asset Hash

Cuando esté disponible, el hash deberá utilizarse para detectar duplicados, cachear análisis, garantizar reproducibilidad y verificar integridad.

---

## 22. Clip

Un clip representa una utilización concreta de un asset:

```typescript
interface Clip {
  id: string;
  assetId: string;
  sourceIn: number;
  sourceOut: number;
  timelineStart: number;
  timelineEnd: number;
  role: ClipRole;
  sceneId?: string;
  segmentId?: string;
}
```

---

## 23. Clip Role

```typescript
type ClipRole =
  | "A_ROLL"
  | "B_ROLL"
  | "TIMELAPSE"
  | "ACTION"
  | "ESTABLISHING"
  | "DETAIL"
  | "TRANSITION"
  | "PHOTO"
  | "SCREEN_CAPTURE";
```

---

## 24. Source Range Invariant

$$0 \le \text{sourceIn} < \text{sourceOut} \le \text{asset.duration}$$

---

## 25. Timeline Range Invariant

$$\text{timelineStart} < \text{timelineEnd}$$

---

## 26. Scene

Una escena representa una unidad narrativa/visual:

```typescript
interface Scene {
  id: string;
  title?: string;
  start: number;
  end: number;
  segmentIds: string[];
  locationId?: string;
  energy?: number;
  tags?: string[];
}
```

---

## 27. Scene Tags

Ejemplos: `arrival`, `food`, `walking`, `hotel`, `museum`, `street`, `night`, `sunset`, `conversation`, `landscape`.

---

## 28. Segment

Un segmento representa una unidad semántica más pequeña:

```typescript
interface Segment {
  id: string;
  sceneId: string;
  start: number;
  end: number;
  transcript?: TranscriptSegment;
  clipIds: string[];
  intent?: SegmentIntent;
}
```

---

## 29. Segment Intent

```typescript
type SegmentIntent =
  | "HOOK"
  | "INTRO"
  | "EXPLANATION"
  | "STORY"
  | "REACTION"
  | "DESCRIPTION"
  | "CTA"
  | "TRANSITION"
  | "OUTRO";
```

---

## 30. Transcript

```typescript
interface TranscriptSegment {
  text: string;
  words: TranscriptWord[];
}
```

---

## 31. Transcript Word

```typescript
interface TranscriptWord {
  id: string;
  text: string;
  start: number;
  end: number;
  confidence?: number;
  emphasis?: boolean;
}
```

---

## 32. Word IDs

Los IDs de palabra deberán ser estables y no depender únicamente de la posición del array.

---

## 33. Language Registry

```typescript
interface LanguageRegistry {
  source: LanguageTrack;
  localized: LanguageTrack[];
}
```

---

## 34. Language Track

```typescript
interface LanguageTrack {
  id: string;
  locale: SupportedLocale;
  transcript?: Transcript;
  voiceover?: VoiceoverTrack;
  subtitles?: SubtitleTrack;
  timelineVariantId?: string;
}
```

---

## 35. Source Language

El idioma original deberá declararse explícitamente (`"locale": "es-MX"`).

---

## 36. Translation

Las traducciones deberán conservar relación con el segmento original:

```typescript
interface TranslationUnit {
  sourceSegmentId: string;
  targetSegmentId: string;
  sourceText: string;
  targetText: string;
}
```

---

## 37. No Independent Translation Timeline

La traducción no deberá crear una línea temporal aislada sin relación con el contenido fuente.

---

## 38. Voiceover Track

```typescript
interface VoiceoverTrack {
  assetId: string;
  locale: SupportedLocale;
  segments: VoiceoverSegment[];
}
```

---

## 39. Voiceover Segment

```typescript
interface VoiceoverSegment {
  segmentId: string;
  assetId: string;
  start: number;
  end: number;
  sourceText?: string;
  targetText?: string;
}
```

---

## 40. B-Roll Assignment

```typescript
interface BRollAssignment {
  segmentId: string;
  clipId: string;
  relevanceScore: number;
  start?: number;
  end?: number;
}
```

---

## 41. Relevance Score

$$\text{score} \in [0, 100]$$

---

## 42. B-Roll Matching

El matcher podrá utilizar: similitud semántica, etiquetas visuales, localización, detección de objetos, tags de escena, palabras clave del transcript y prioridad manual.

---

## 43. Manual Priority

Una asignación manual deberá poder bloquear una decisión automática (`locked: boolean`).

---

## 44. Auto Assignment

Si `locked = false`, el pipeline podrá recalcular el B-roll automáticamente.

---

## 45. A-Roll

```typescript
interface ARollAnalysis {
  clipId: string;
  speakerDetected: boolean;
  faceRegions: FaceRegion[];
  speechRegions: SpeechRegion[];
  confidence: number;
}
```

---

## 46. B-Roll Analysis

```typescript
interface BRollAnalysis {
  clipId: string;
  labels: string[];
  objects?: string[];
  locationId?: string;
  motionLevel?: number;
  visualEnergy?: number;
}
```

---

## 47. Silence Regions

```typescript
interface SilenceRegion {
  start: number;
  end: number;
  duration: number;
  removable: boolean;
}
```

---

## 48. Jump Cut Decision

```typescript
interface JumpCutDecision {
  id: string;
  clipId: string;
  start: number;
  end: number;
  action: "REMOVE" | "KEEP";
  reason: string;
}
```

---

## 49. Punch-In Decision

```typescript
interface PunchInDecision {
  id: string;
  segmentId: string;
  start: number;
  end: number;
  scale: number;
  anchor: "FACE" | "EYES" | "CENTER";
}
```

---

## 50. Default Punch-In

$100\%$ normal $\to 115\%$ énfasis (configurable).

---

## 51. Timeline

```typescript
interface Timeline {
  id: string;
  locale: SupportedLocale;
  duration: number;
  clips: TimelineClip[];
  events: TimelineEvent[];
}
```

---

## 52. Timeline Clip

```typescript
interface TimelineClip {
  clipId: string;
  start: number;
  end: number;
  sourceIn: number;
  sourceOut: number;
}
```

---

## 53. Timeline Event

```typescript
interface TimelineEvent {
  id: string;
  type: string;
  start: number;
  end?: number;
  payload?: Record<string, unknown>;
}
```

---

## 54. Semantic Events

Los eventos deberán preferir referencias semánticas (`segmentId`, `wordId`, `shotId`, `overlayId`, `transitionId`) sobre timestamps absolutos cuando sea posible.

---

## 55. Transition

```typescript
interface TransitionEvent {
  id: string;
  type:
    | "CUT"
    | "CROSSFADE"
    | "ZOOM"
    | "FLASH"
    | "SLIDE"
    | "WHIP_PAN"
    | "GLITCH"
    | "IRIS";
  start: number;
  duration: number;
}
```

---

## 56. Audio Configuration

```typescript
interface AudioProjectConfig {
  music?: MusicConfig;
  ducking: DuckingConfig;
  sfxEnabled: boolean;
  ambienceEnabled: boolean;
  master: MasterAudioSettings;
}
```

---

## 57. Subtitle Configuration

```typescript
interface SubtitleProjectConfig {
  enabled: boolean;
  maxWordsPerLine: number;
  maxWidth: number;
  stylePreset: string;
  karaoke: boolean;
  emojis: boolean;
}
```

---

## 58. Overlay Configuration

```typescript
interface OverlayProjectConfig {
  enabled: boolean;
  safeZones: SafeZone;
  overlays: TravelOverlay[];
}
```

---

## 59. Location Registry

```typescript
interface LocationRegistry {
  locations: Location[];
}
```

---

## 60. Location

```typescript
interface Location {
  id: string;
  name: string;
  city?: string;
  region?: string;
  country?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
}
```

---

## 61. Location Data Integrity

Si se proporcionan coordenadas:
$$\text{latitude} \in [-90, 90], \quad \text{longitude} \in [-180, 180]$$

---

## 62. Location Aliases

Una ubicación podrá tener alias para búsqueda semántica (`aliases?: string[];`).

---

## 63. Timezone

Identificador IANA válido (ej. `America/Mexico_City`).

---

## 64. Style Configuration

```typescript
interface StyleConfiguration {
  presetId: string;
  overrides?: Record<string, unknown>;
}
```

---

## 65. Preset Hierarchy

$$\text{Global} \longrightarrow \text{Project} \longrightarrow \text{Scene} \longrightarrow \text{Segment} \longrightarrow \text{Element} \quad (\text{El nivel más específico gana})$$

---

## 66. Export Configuration

```typescript
interface ExportConfig {
  formats: ExportFormat[];
  compositions: CompositionConfig[];
  generateAE: boolean;
  generateMetadata: boolean;
}
```

---

## 67. Composition

```typescript
interface CompositionConfig {
  id: string;
  locale: SupportedLocale;
  aspectRatio: AspectRatio;
  resolution: Resolution;
  fps: number;
  duration: number;
}
```

---

## 68. Multilingual Composition

Composición independiente por idioma: `VLOG_ES`, `VLOG_EN`, `VLOG_PT`, `VLOG_FR`, `VLOG_DE`.

---

## 69. Multilingual Independence

Cambiar el idioma modifica voz, subtítulos, overlays y duraciones sin alterar la identidad semántica del proyecto.

---

## 70. Variant System

```typescript
interface ProjectVariant {
  id: string;
  locale: SupportedLocale;
  aspectRatio: AspectRatio;
  presetId: string;
  timelineId: string;
}
```

---

## 71. Example Variants

- `es-MX / 16:9 / Travel`
- `es-MX / 9:16 / Travel`
- `en-US / 16:9 / Documentary`
- `en-US / 9:16 / Shorts`
- `pt-BR / 9:16 / Travel`

---

## 72. Variant Matrix

$$\text{Languages} \times \text{Aspect Ratios} \times \text{Presets}$$

---

## 73. Constraint Resolution

Si una combinación es inválida, se emite error o advertencia antes de generar una salida corrupta.

---

## 74. Render Profile

```typescript
interface RenderProfile {
  id: string;
  codec: string;
  container: string;
  bitrate?: number;
  audioCodec?: string;
}
```

---

## 75. Cache

Estructura de caché en directorios aislados: `analysis/`, `transcription/`, `classification/`, `voiceover/`, `timelines/`, `audio/`, `overlays/`, `exports/`.

---

## 76. Cache Key

$$\text{hash}(\text{assetHash} + \text{moduleVersion} + \text{configHash} + \text{schemaVersion})$$

---

## 77. Invalidación de Cache

Modificar un parámetro invalida únicamente los artefactos dependientes directos.

---

## 78. Pipeline State

```typescript
type PipelineStage =
  | "INGESTION"
  | "TRANSCRIPTION"
  | "CLASSIFICATION"
  | "EDITING"
  | "LOCALIZATION"
  | "VOICEOVER"
  | "PACING"
  | "AUDIO"
  | "OVERLAYS"
  | "SUBTITLES"
  | "REFRAME"
  | "EXPORT"
  | "VALIDATION";
```

---

## 79. Stage Status

```typescript
interface StageStatus {
  stage: PipelineStage;
  status: "PENDING" | "RUNNING" | "SUCCESS" | "FAILED" | "SKIPPED";
  startedAt?: string;
  endedAt?: string;
  errors?: string[];
  warnings?: string[];
}
```

---

## 80. Idempotency

Ejecutar dos veces una etapa con la misma entrada produce el mismo resultado.

---

## 81. Failure Recovery

Una etapa fallida no obliga a repetir etapas anteriores cuyos outputs sigan siendo válidos.

---

## 82. Checkpoint

Cada etapa produce un checkpoint intermedio `stage-output.json`.

---

## 83. Validation Root

$$\text{Project} \longrightarrow \text{Schema Val} \longrightarrow \text{Semantic Val} \longrightarrow \text{Timeline Val} \longrightarrow \text{Asset Val} \longrightarrow \text{Export}$$

---

## 84. Schema Validation

Verificación de tipos, campos requeridos, enums, formatos y referencias cruzadas.

---

## 85. Referential Integrity

Todo `assetId`, `clipId`, `sceneId`, `segmentId`, `locationId`, `overlayId`, `wordId` y `timelineId` debe apuntar a una entidad existente.

---

## 86. Orphan Detection

Detección de entidades huérfanas sin referencias activas.

---

## 87. Circular Dependency

Detección de ciclos en referencias jerárquicas.

---

## 88. Timeline Invariants

Nunca duraciones negativas, rangos inválidos de fuente o solapamientos de clips exclusivos.

---

## 89. Semantic Invariants

Cada segmento pertenece a una escena; cada escena se localiza dentro del timeline.

---

## 90. Localization Invariants

Cada idioma habilitado dispone de traducción, locución y subtítulos requeridos.

---

## 91. Optional Localization

Si un idioma opcional falla, el proyecto base continúa su generación.

---

## 92. Required Asset

```typescript
interface AssetReference {
  assetId: string;
  required: boolean;
}
```

---

## 93. Manual Lock

```typescript
interface LockableDecision {
  locked: boolean;
  lockedBy?: "USER" | "SYSTEM";
}
```

---

## 94. Human Override

Soporte para reemplazar manualmente decisiones de B-roll, cortes, punch-ins, música o subtítulos sin destruir el pipeline.

---

## 95. Override Precedence

$$\text{USER LOCK} > \text{EXPLICIT CONFIG} > \text{AUTOMATIC DECISION} > \text{DEFAULT}$$

---

## 96. Audit Trail

Registro estructurado de decisiones automáticas (`DecisionRecord`).

---

## 97. Explainability

Explicación explícita de descartes de clips (baja calidad, falta de duración, duplicado, etc.).

---

## 98. Confidence

$$\text{confidence} \in [0.0, 1.0]$$

---

## 99. Confidence Thresholds

```typescript
interface ConfidenceThreshold {
  automatic: number;
  warning: number;
}
```

---

## 100. Low Confidence

Baja confianza emite warning o solicita revisión humana según configuración.

---

## 101. DSL

Sintaxis declarativa de alto nivel:

```dsl
PROJECT "Guadalajara Vlog"

SOURCE_LANGUAGE es-MX

SCENE "Centro Histórico" {
  LOCATION "centro_guadalajara"

  SEGMENT "intro" {
    INTENT INTRO
    A_ROLL "clip_001"
    B_ROLL AUTO
    GEO_BADGE ENABLED
  }
}
```

---

## 102. DSL Principle

Declarativa, determinista, versionable, serializable y validable.

---

## 103. JSON as Canonical Representation

$$\text{DSL} \longrightarrow \text{Parser} \longrightarrow \text{AST} \longrightarrow \text{Validator} \longrightarrow \text{Canonical JSON}$$

---

## 104. No Dual Truth

La DSL y el JSON representan exactamente la misma semántica.

---

## 105. DSL Validation

Errores con indicación de línea, columna, propiedad y valor esperado.

---

## 106. Serialization

JSON canónico con orden estable de claves para hashing.

---

## 107. Project Hash

$$\text{projectHash} = \text{SHA-256}(\text{canonical JSON})$$

---

## 108. Deterministic Build

Mismo hash y versiones de motor producen outputs binariamente o semánticamente idénticos.

---

## 109. Reproducibility Manifest

`reproducibility.json` registra hashes de proyecto, módulos y assets.

---

## 110. Security

Validación de rutas externas para evitar Path Traversal (`../`).

---

## 111. Path Traversal

Bloqueo estricto de escapes de directorio.

---

## 112. Script Safety

El proyecto JSON nunca ejecuta código arbitrario.

---

## 113. JSX Separation

El parser del proyecto nunca interpreta código JSX de After Effects.

---

## 114. MCP Integration

Operaciones MCP disponibles: `createProject`, `readProject`, `validateProject`, `updateProject`, `runStage`, `exportProject`.

---

## 115. Partial Updates

Actualizaciones parciales de entidades concretas sin reconstruir todo el árbol.

---

## 116. Transactional Updates

Actualizaciones atómicas con reversión en caso de error.

---

## 117. Migration

Estrategia formal de migración ante cambios de esquema.

---

## 118. Backward Compatibility

Versiones menores sin romper compatibilidad existente.

---

## 119. Migration Example

$$1.0.0 \to 1.1.0 \quad (\text{compatible}), \quad 1.x \to 2.0.0 \quad (\text{requiere migrador})$$

---

## 120. Test Suite

Cobertura de parsing, validación de schema, integridad referencial, serialización, DSL, hashing y transacciones.

---

## 121. Property-Based Tests

$$\text{serialize}(\text{parse}(x)) \equiv \text{canonical}(x)$$

---

## 122. Round-Trip Test

$$\text{JSON} \longrightarrow \text{parse} \longrightarrow \text{serialize} \longrightarrow \text{parse} \quad (\text{cero pérdida})$$

---

## 123. Invalid Project Tests

Cobertura de IDs faltantes o duplicados, rangos inválidos y referencias rotas.

---

## 124. DSL Snapshot Tests

Snapshots para ejemplos oficiales de DSL.

---

## 125. Canonical JSON Test

Dos proyectos equivalentes generan idéntico JSON canónico.

---

## 126. Hash Test

Idéntico JSON canónico genera exactamente el mismo hash SHA-256.

---

## 127. No Runtime Clock

Independencia de la hora del sistema en tiempo de compilación.

---

## 128. No Network

Validación y compilación ejecutables 100% offline.

---

## 129. No Hidden Defaults

Todos los valores por defecto residen documentados en el schema o presets.

---

## 130. Configuration Precedence

$$\text{USER OVERRIDE} \longrightarrow \text{VARIANT} \longrightarrow \text{PROJECT} \longrightarrow \text{SCENE} \longrightarrow \text{SEGMENT} \longrightarrow \text{PRESET} \longrightarrow \text{GLOBAL DEFAULT}$$

---

## 131. Definition of Done

- [ ] Project root schema
- [ ] Schema version
- [ ] Engine version
- [ ] Project metadata
- [ ] Project settings
- [ ] Locale system
- [ ] Aspect ratios
- [ ] Resolution
- [ ] FPS
- [ ] Asset registry
- [ ] Asset hashing
- [ ] Clip schema
- [ ] Scene schema
- [ ] Segment schema
- [ ] Transcript schema
- [ ] Word IDs
- [ ] Language registry
- [ ] Translation units
- [ ] Voiceover schema
- [ ] A-Roll analysis
- [ ] B-Roll analysis
- [ ] B-Roll assignments
- [ ] Jump-cut decisions
- [ ] Punch-in decisions
- [ ] Timeline schema
- [ ] Transition schema
- [ ] Audio schema
- [ ] Subtitle schema
- [ ] Overlay schema
- [ ] Location registry
- [ ] Timezone handling
- [ ] Style configuration
- [ ] Preset hierarchy
- [ ] Export configuration
- [ ] Composition variants
- [ ] Multilingual variants
- [ ] Cache
- [ ] Cache invalidation
- [ ] Pipeline stages
- [ ] Checkpoints
- [ ] Schema validation
- [ ] Referential integrity
- [ ] Orphan detection
- [ ] Circular dependency detection
- [ ] Semantic validation
- [ ] Manual locks
- [ ] Human overrides
- [ ] Audit trail
- [ ] Confidence
- [ ] DSL
- [ ] DSL parser
- [ ] DSL compiler
- [ ] Canonical JSON
- [ ] Project hash
- [ ] Reproducibility manifest
- [ ] Path security
- [ ] MCP integration
- [ ] Partial updates
- [ ] Transactional updates
- [ ] Schema migration
- [ ] Unit tests
- [ ] Property tests
- [ ] Round-trip tests
- [ ] Snapshot tests
- [ ] Offline tests
- [ ] Deterministic tests

---

## 132. Estado Final

**Documento:** `13-VLOG-PROJECT-SCHEMA-AND-DECLARATIVE-DSL.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

---

## 133. Regla de Implementación

Este documento deberá considerarse una dependencia contractual de todos los documentos posteriores. Ningún módulo nuevo podrá definir una estructura de datos incompatible con este schema sin actualizar este documento, incrementar la versión del schema, documentar la migración y actualizar las pruebas y el MCP.

---

## 134. Fuente de Verdad Definitiva

```
                VLOG PROJECT
                     │
                     ▼
          CANONICAL PROJECT SCHEMA
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
     ANALYSIS     DECISIONS     OUTPUTS
        │            │            │
        ▼            ▼            ▼
     A-Roll        Timeline       AE JSX
     B-Roll        Audio          Video
     Transcript    Overlays       Metadata
     Location      Subtitles      Social Pack
     Language      Reframe
```

Todo el sistema deberá converger hacia este contrato.
