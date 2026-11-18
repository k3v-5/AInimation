# Data Contracts — Vlog Intelligence Engine

**Documento:** `02-DATA-CONTRACTS.md`  
**Versión:** `1.0.0`  
**Sistema:** Motor audiovisual v3.4.0 + Vlog Multilingual Expansion  
**Estado:** DRAFT  
**Implementación autorizada:** NO hasta aprobación  
**Dependencia:** `00-MASTER-SPECIFICATION.md` + `01-ARCHITECTURE.md`  

---

## 1. Propósito

Este documento define los contratos de datos utilizados por todos los módulos de la expansión Vlog Multilingüe.

Los contratos constituyen la interfaz formal entre componentes.

Ningún módulo deberá asumir estructuras, unidades, valores por defecto o semánticas que no estén definidas aquí o en un contrato derivado aprobado.

---

## 2. Principios

Todos los contratos deberán cumplir:
- Tipado explícito.
- Unidades explícitas.
- Rangos explícitos.
- Campos obligatorios definidos.
- Campos opcionales definidos.
- Valores por defecto documentados.
- Validación.
- Versionado.
- Serialización determinista.
- Compatibilidad hacia atrás cuando sea posible.
- Rechazo explícito de datos inválidos.

---

## 3. Convenciones

### 3.1. Tiempo
Todo tiempo interno utilizará:
$$\text{seconds}$$
como unidad lógica.

Los valores podrán representarse mediante `number`, siempre que el contrato de precisión sea respetado.

Ejemplo:
```typescript
const time = 12.345678;
```

No se utilizarán `frames`, `milliseconds` ni `ticks` como unidad principal de dominio. Podrán utilizarse únicamente en adaptadores.

---

## 4. Convención temporal

Todos los intervalos utilizarán:
$$[t_{\text{start}}, t_{\text{end}})$$

Por tanto:
$$\text{duration} = \text{end} - \text{start}$$
y siempre deberá cumplirse:
$$\text{end} \ge \text{start}$$

Un segmento de duración cero sólo podrá existir cuando el contrato específico lo permita.

---

## 5. Identificadores

Los IDs serán strings:
```typescript
type EntityId = string;
```

Deberán ser:
- únicos dentro de su namespace.
- deterministas cuando representen resultados derivados.
- estables durante una ejecución.
- serializables.

No deberán depender de memoria, orden accidental de objetos ni valores aleatorios.

---

## 6. Versionado de contratos

Todos los documentos serializables deberán tener:
```typescript
schemaVersion: string; // ej. "1.0.0"
```

La versión del schema representa la estructura del contrato. La versión del algoritmo será independiente.

---

## 7. PipelineContext

Representa el contexto global de una ejecución.

```typescript
interface PipelineContext {
  schemaVersion: string;

  executionId: string;
  projectId: string;
  sourceId: string;

  engineVersion: string;
  configurationVersion: string;

  deterministicSeed: number;

  createdAt?: string;
}
```

### Reglas
- `executionId` deberá identificar una ejecución.
- `projectId` deberá identificar el proyecto.
- `sourceId` deberá identificar el material fuente.
- `deterministicSeed` deberá permanecer estable durante la ejecución.
- `createdAt` será metadata y no deberá utilizarse como entrada de algoritmos deterministas.

---

## 8. MediaReference

Representa una fuente audiovisual.

```typescript
interface MediaReference {
  schemaVersion: string;

  id: string;

  path: string;

  contentHash?: string;

  duration: number;

  width: number;
  height: number;

  frameRate: number;

  videoCodec?: string;

  audioTracks: AudioTrackReference[];

  metadata?: Record<string, unknown>;
}
```

### Invariantes
$$\text{duration} \ge 0, \quad \text{width} > 0, \quad \text{height} > 0, \quad \text{frameRate} > 0$$
Las dimensiones deberán ser enteros positivos.

---

## 9. AudioTrackReference

```typescript
interface AudioTrackReference {
  id: string;

  channels: number;
  sampleRate: number;

  duration: number;

  language?: string;

  role:
    | "ORIGINAL_VOICE"
    | "LOCALIZED_VOICE"
    | "MUSIC"
    | "SFX"
    | "AMBIENT"
    | "UNKNOWN";
}
```

---

## 10. TimeRange

Contrato base para intervalos.

```typescript
interface TimeRange {
  start: number;
  end: number;
}
```

### Invariante
$$\text{start} \ge 0, \quad \text{end} \ge \text{start}$$

---

## 11. SpeechState

```typescript
type SpeechState =
  | "SPEECH"
  | "NON_SPEECH"
  | "UNKNOWN";
```

---

## 12. SpeechSegment

```typescript
interface SpeechSegment extends TimeRange {
  id: string;

  state: SpeechState;

  confidence: number;

  audioTrackId: string;
}
```

### Invariante
$$0 \le \text{confidence} \le 1$$

---

## 13. SilenceSegment

```typescript
interface SilenceSegment extends TimeRange {
  id: string;

  duration: number;

  confidence: number;

  source: "VAD" | "AUDIO_ENERGY" | "HYBRID";
}
```

La duración deberá coincidir con $\text{end} - \text{start}$. No deberá almacenarse una duración contradictoria.

---

## 14. WordTiming

Unidad mínima de sincronización lingüística.

```typescript
interface WordTiming extends TimeRange {
  id: string;

  text: string;

  normalizedText?: string;

  confidence: number;

  speakerId?: string;
}
```

### Invariantes
$$\text{text.length} > 0, \quad 0 \le \text{confidence} \le 1, \quad \text{end} \ge \text{start}$$

---

## 15. Transcript

```typescript
interface Transcript {
  schemaVersion: string;

  id: string;

  language: string;

  words: WordTiming[];

  segments: TranscriptSegment[];

  provider: string;

  providerVersion?: string;
}
```

---

## 16. TranscriptSegment

```typescript
interface TranscriptSegment extends TimeRange {
  id: string;

  text: string;

  wordIds: string[];

  confidence: number;

  speakerId?: string;
}
```

Los `wordIds` deberán referenciar palabras existentes dentro del transcript.

---

## 17. AudioAnalysis

```typescript
interface AudioAnalysis {
  schemaVersion: string;

  id: string;

  trackId: string;

  duration: number;

  rms: AudioLevelSample[];

  peaks: AudioPeak[];

  speechSegments: SpeechSegment[];

  silenceSegments: SilenceSegment[];
}
```

---

## 18. AudioLevelSample

```typescript
interface AudioLevelSample {
  time: number;

  rms: number;
}
```

El RMS deberá ser $\text{rms} \ge 0$.

---

## 19. AudioPeak

```typescript
interface AudioPeak {
  time: number;

  amplitude: number;

  confidence: number;
}
```

---

## 20. Shot

Representa una unidad visual detectada.

```typescript
interface Shot extends TimeRange {
  id: string;

  sourceMediaId: string;

  index: number;

  width: number;
  height: number;

  motionScore?: number;

  visualConfidence?: number;

  classification?: FootageClassification;

  focusPoints?: FocusPoint[];

  semanticTags?: SemanticTag[];
}
```

---

## 21. ShotManifest

```typescript
interface ShotManifest {
  schemaVersion: string;

  sourceMediaId: string;

  shots: Shot[];

  analysisVersion: string;
}
```

Los shots deberán estar ordenados temporalmente.

---

## 22. FootageClassification

```typescript
type FootageClassification =
  | "A_ROLL"
  | "B_ROLL"
  | "TIMELAPSE"
  | "ACTION"
  | "UNKNOWN";
```

---

## 23. ClassificationResult

```typescript
interface ClassificationResult {
  classification: FootageClassification;

  confidence: number;

  scores: {
    aRoll: number;
    bRoll: number;
    timelapse: number;
    action: number;
  };

  reasons: ClassificationReason[];
}
```

Todos los scores deberán estar normalizados: $0 \le \text{score} \le 1$.

---

## 24. ClassificationReason

```typescript
interface ClassificationReason {
  type:
    | "FACE_PRESENCE"
    | "SPEECH_ACTIVITY"
    | "CAMERA_MOTION"
    | "TEMPORAL_PATTERN"
    | "VISUAL_CONTENT"
    | "AUDIO_PATTERN"
    | "OTHER";

  weight: number;

  description: string;
}
```

Los motivos deberán ser explicables y deterministas.

---

## 25. FocusPoint

Representa un punto de interés visual. Las coordenadas serán normalizadas.

```typescript
interface FocusPoint {
  x: number;
  y: number;

  confidence: number;

  source:
    | "EYES"
    | "FACE"
    | "OBJECT"
    | "CENTER"
    | "MANUAL";
}
```

### Rango
$$0 \le x \le 1, \quad 0 \le y \le 1$$
Esto permite independencia respecto a resolución.

---

## 26. PunchInEvent

```typescript
interface PunchInEvent extends TimeRange {
  id: string;

  scale: number;

  focusPoint: FocusPoint;

  easing: EasingDefinition;

  reason: PunchInReason;
}
```

---

## 27. PunchInReason

```typescript
type PunchInReason =
  | "TOPIC_CHANGE"
  | "EMPHASIS"
  | "HOOK"
  | "ENERGY_CHANGE"
  | "MANUAL"
  | "OTHER";
```

---

## 28. EasingDefinition

```typescript
interface EasingDefinition {
  type:
    | "LINEAR"
    | "BEZIER"
    | "EASE_IN"
    | "EASE_OUT"
    | "EASE_IN_OUT";

  parameters?: number[];
}
```

Los parámetros deberán ser validados según el tipo.

---

## 29. SemanticTag

```typescript
interface SemanticTag {
  id: string;

  label: string;

  category:
    | "LOCATION"
    | "FOOD"
    | "PERSON"
    | "OBJECT"
    | "ACTIVITY"
    | "TRANSPORT"
    | "ARCHITECTURE"
    | "NATURE"
    | "EVENT"
    | "OTHER";

  confidence: number;
}
```

---

## 30. BrollMatch

Representa la relación entre discurso y B-Roll.

```typescript
interface BrollMatch {
  id: string;

  speechSegmentId: string;

  candidateShotIds: string[];

  selectedShotId?: string;

  score: number;

  reasons: BrollMatchReason[];
}
```

---

## 31. BrollMatchReason

```typescript
interface BrollMatchReason {
  type:
    | "SEMANTIC"
    | "TEMPORAL"
    | "VISUAL"
    | "LOCATION"
    | "DIVERSITY"
    | "QUALITY";

  score: number;

  explanation: string;
}
```

---

## 32. EditSegment

Unidad básica del montaje.

```typescript
interface EditSegment extends TimeRange {
  id: string;

  sourceMediaId: string;

  sourceRange: TimeRange;

  role:
    | "A_ROLL"
    | "B_ROLL"
    | "TIMELAPSE"
    | "ACTION"
    | "GRAPHICS";

  trackId: string;

  transitionIn?: TransitionReference;
  transitionOut?: TransitionReference;

  effects?: EffectReference[];
}
```

---

## 33. TransitionReference

```typescript
interface TransitionReference {
  type:
    | "CUT"
    | "CROSSFADE"
    | "ZOOM"
    | "FLASH"
    | "SLIDE"
    | "WHIP_PAN"
    | "GLITCH"
    | "IRIS";

  duration: number;
}
```

---

## 34. EffectReference

```typescript
interface EffectReference {
  type:
    | "PUNCH_IN"
    | "COLOR"
    | "BLUR"
    | "GRAIN"
    | "GLOW"
    | "SHAKE"
    | "CUSTOM";

  parameters: Record<string, unknown>;
}
```

---

## 35. AudioEvent

```typescript
interface AudioEvent extends TimeRange {
  id: string;

  trackId: string;

  type:
    | "VOICE"
    | "MUSIC"
    | "SFX"
    | "AMBIENT";

  gainDb?: number;

  source?: string;
}
```

---

## 36. LocalizationLanguage

```typescript
type LocalizationLanguage =
  | "es-MX"
  | "es-ES"
  | "en-US"
  | "en-GB"
  | "pt-BR"
  | "fr-FR"
  | "de-DE";
```

El sistema deberá poder extender esta lista mediante mecanismos documentados.

---

## 37. LocalizedText

```typescript
interface LocalizedText {
  language: string;

  sourceTextId: string;

  text: string;

  wordTimings?: WordTiming[];

  duration?: number;
}
```

---

## 38. TTSRequest

```typescript
interface TTSRequest {
  language: LocalizationLanguage;

  text: string;

  voiceId: string;

  speakingRate?: number;

  pitch?: number;

  outputFormat: "WAV_PCM_16";
}
```

---

## 39. TTSResult

```typescript
interface TTSResult {
  schemaVersion: string;

  requestId: string;

  language: LocalizationLanguage;

  voiceId: string;

  audioPath: string;

  duration: number;

  sampleRate: number;

  channels: number;

  wordTimings?: WordTiming[];

  provider: string;

  providerVersion?: string;
}
```

El formato inicial obligatorio será PCM 16-bit WAV. Los parámetros exactos de sample rate y canales deberán quedar definidos por el módulo TTS.

---

## 40. LocalizationTrack

```typescript
interface LocalizationTrack {
  id: string;

  language: LocalizationLanguage;

  sourceLanguage: LocalizationLanguage;

  audio: TTSResult;

  transcript: Transcript;

  duration: number;
}
```

---

## 41. LocalizationPlan

```typescript
interface LocalizationPlan {
  schemaVersion: string;

  sourceLanguage: LocalizationLanguage;

  targetLanguages: LocalizationLanguage[];

  tracks: LocalizationTrack[];

  timingStrategy: TimingStrategy;
}
```

---

## 42. TimingStrategy

```typescript
type TimingStrategy =
  | "VISUAL_FIRST"
  | "VOICE_FIRST"
  | "HYBRID";
```

La estrategia concreta por proyecto deberá quedar registrada.

---

## 43. PacingAdjustment

```typescript
interface PacingAdjustment {
  id: string;

  targetId: string;

  originalDuration: number;

  adjustedDuration: number;

  factor: number;

  method:
    | "CLIP_EXTENSION"
    | "CLIP_TRIM"
    | "VOICE_STRETCH"
    | "VOICE_COMPRESS"
    | "RESELECTION";
}
```

---

## 44. Overlay

```typescript
interface Overlay extends TimeRange {
  id: string;

  type:
    | "GEO_BADGE"
    | "ROUTE_MAP"
    | "POLAROID"
    | "TIMESTAMP"
    | "LOCATION_CARD";

  parameters: Record<string, unknown>;

  stylePreset?: string;
}
```

Los overlays serán puramente declarativos y no contendrán código JSX directo.

---

## 45. GeoBadge

```typescript
interface GeoBadgeParameters {
  latitude?: number;
  longitude?: number;

  city?: string;
  region?: string;
  country?: string;

  timestamp?: string;

  label?: string;
}
```

### Invariantes
$$-90 \le \text{latitude} \le 90, \quad -180 \le \text{longitude} \le 180$$

---

## 46. RouteMap

```typescript
interface RouteMapParameters {
  points: GeoPoint[];

  animated: boolean;

  duration?: number;
}
```

---

## 47. GeoPoint

```typescript
interface GeoPoint {
  latitude: number;
  longitude: number;
}
```

---

## 48. PolaroidParameters

```typescript
interface PolaroidParameters {
  frameTime: number;

  frameWidth: number;
  frameHeight: number;

  rotation: number;

  shadow: boolean;

  shutterSfx?: string;
}
```

---

## 49. GraphicsPlan

```typescript
interface GraphicsPlan {
  schemaVersion: string;

  overlays: Overlay[];
}
```

---

## 50. EditPlan

Es el contrato principal de salida editorial.

```typescript
interface EditPlan {
  schemaVersion: string;

  id: string;

  projectId: string;

  sourceMedia: MediaReference;

  duration: number;

  videoTracks: VideoTrack[];

  audioTracks: AudioPlan[];

  segments: EditSegment[];

  graphics: GraphicsPlan;

  localization?: LocalizationPlan;

  metadata: EditMetadata;
}
```

---

## 51. VideoTrack

```typescript
interface VideoTrack {
  id: string;

  index: number;

  role:
    | "PRIMARY"
    | "BROLL"
    | "GRAPHICS"
    | "OVERLAY";

  segments: string[];
}
```

Los IDs deberán referenciar `EditSegment`.

---

## 52. AudioPlan

```typescript
interface AudioPlan {
  id: string;

  index: number;

  role:
    | "ORIGINAL_VOICE"
    | "LOCALIZED_VOICE"
    | "MUSIC"
    | "SFX"
    | "AMBIENT";

  events: AudioEvent[];
}
```

---

## 53. EditMetadata

```typescript
interface EditMetadata {
  engineVersion: string;

  configurationVersion: string;

  analysisVersions: Record<string, string>;

  algorithmVersions: Record<string, string>;

  deterministicSeed: number;

  generatedAt?: string;
}
```

`generatedAt` será informativo y no deberá participar en hashes deterministas.

---

## 54. DecisionRecord

Toda decisión editorial importante podrá registrar:

```typescript
interface DecisionRecord {
  id: string;

  type: string;

  inputIds: string[];

  decision: string;

  score?: number;

  reasons: string[];

  configuration: Record<string, unknown>;
}
```

---

## 55. PipelineArtifact

```typescript
interface PipelineArtifact {
  id: string;

  type:
    | "MEDIA_ANALYSIS"
    | "AUDIO_ANALYSIS"
    | "TRANSCRIPT"
    | "SHOT_MANIFEST"
    | "EDIT_PLAN"
    | "TTS"
    | "LOCALIZATION"
    | "GRAPHICS"
    | "EXPORT";

  schemaVersion: string;

  producer: string;

  producerVersion: string;

  contentHash?: string;
}
```

---

## 56. Errores

Todos los errores estructurados deberán utilizar:

```typescript
interface PipelineError {
  code: string;

  severity:
    | "FATAL"
    | "RECOVERABLE"
    | "WARNING"
    | "INFO";

  message: string;

  module: string;

  details?: Record<string, unknown>;

  causeCode?: string;
}
```

No se deberá depender exclusivamente de mensajes de texto para determinar el tipo de error.

---

## 57. Códigos de error

Los códigos deberán seguir el patrón:
$$\text{<VERTICAL>\_<MODULE>\_<NUMBER>}$$

Ejemplos:
- `VLOG_MEDIA_001`
- `VLOG_VAD_001`
- `VLOG_TRANSCRIPT_001`
- `VLOG_JUMPCUT_001`
- `VLOG_PUNCHIN_001`
- `VLOG_BROLL_001`
- `VLOG_TTS_001`
- `VLOG_PACING_001`
- `VLOG_OVERLAY_001`
- `VLOG_EXPORT_001`

---

## 58. Validación

Todos los contratos externos deberán validarse antes de entrar al dominio:
- tipos.
- presencia.
- rangos.
- referencias.
- timestamps.
- IDs.
- enums.
- versiones.

---

## 59. Referencias

Los contratos que utilicen IDs deberán validar que las referencias existan:
$$\text{BrollMatch.selectedShotId} \longrightarrow \text{ShotManifest.shots[].id}$$

Una referencia inexistente será un error de contrato estricto.

---

## 60. Integridad temporal

Los siguientes requisitos son obligatorios:
$$\text{start} \ge 0, \quad \text{end} \ge \text{start}, \quad \text{duration} = \text{end} - \text{start}$$

Cuando existan segmentos consecutivos:
$$\text{segment}[i].\text{end} \le \text{segment}[i+1].\text{start}$$
salvo que el contrato permita explícitamente solapamientos.

---

## 61. Solapamientos

Los solapamientos no están prohibidos globalmente; dependen del tipo de track:
- `A-Roll + B-Roll`: permite composición visual superpuesta.
- Dos segmentos en track `PRIMARY`: conflicto temporal estricto.

Cada track deberá declarar su política.

---

## 62. Normalización

Antes de almacenar datos en dominio deberán normalizarse:
- idiomas.
- enums.
- rutas.
- timestamps.
- valores numéricos.
- texto cuando corresponda.

La normalización no deberá modificar el significado semántico.

---

## 63. Serialización determinista

Cuando un objeto de dominio sea serializado:
- las claves deberán tener orden estable.
- arrays deberán tener orden definido.
- valores flotantes deberán utilizar representación consistente.
- campos opcionales no deberán aparecer/desaparecer arbitrariamente.

El serializador deberá ser testeable.

---

## 64. Hashes

Cuando se utilicen hashes:
$$\text{hash}(\text{input} + \text{relevant configuration} + \text{algorithm version})$$
deberá producir una identidad reproducible. Los campos puramente informativos como timestamps de ejecución deberán excluirse cuando no formen parte del contenido lógico.

---

## 65. Compatibilidad

### Cambios compatibles:
- agregar campos opcionales.
- agregar nuevos enums cuando los consumidores los toleren.
- agregar metadata no esencial.

### Cambios incompatibles:
- cambiar unidades.
- cambiar semántica temporal.
- cambiar tipos.
- renombrar campos obligatorios.
- cambiar significado de un enum.

Los cambios incompatibles requerirán una nueva versión mayor del contrato.

---

## 66. No almacenar decisiones implícitas

No se deberá depender de `undefined = default X`, `0 = disabled` o `-1 = automatic` salvo que esté definido explícitamente. Los estados ambiguos deberán representarse explícitamente.

---

## 67. Configuración vs resultado

No deberán mezclarse `Configuration` con `Result`.

*Ejemplo incorrecto:*
```typescript
// INCORRECTO:
interface SilenceSegment {
  threshold: 0.25; // El threshold pertenece a la configuración o DecisionRecord
}
```

El segmento representa el resultado detectado; el umbral pertenece a la configuración.

---

## 68. Fuente vs derivado

Todo dato deberá poder clasificarse como:
- `SOURCE` (ej. Video file)
- `DERIVED` (ej. Transcript)
- `DECISION` (ej. B-Roll selection)
- `OUTPUT` (ej. EditPlan)

---

## 69. Inmutabilidad lógica

Los siguientes objetos serán tratados como snapshots inmutables:
- `MediaReference`
- `Transcript`
- `ShotManifest`
- `AudioAnalysis`
- `ClassificationResult`
- `TTSResult`

Las transformaciones producirán nuevas versiones.

---

## 70. Contrato entre Analysis y Editorial

Analysis producirá:
- `AudioAnalysis`
- `Transcript`
- `ShotManifest`
- `ClassificationResult`
- `SemanticTag[]`
- `FocusPoint[]`

Editorial consumirá esos contratos. Editorial no deberá acceder directamente a datos internos de los analizadores.

---

## 71. Contrato entre Editorial y Export

Editorial producirá:
- `EditPlan`
- `GraphicsPlan`
- `LocalizationPlan`

Export consumirá estos objetos. Export no deberá ejecutar análisis.

---

## 72. Contrato entre TTS y Pacing

TTS deberá proporcionar:
- `audio duration`
- `word timings`
- `language`
- `voice metadata`

Pacing deberá poder calcular $\text{visual duration} \leftrightarrow \text{speech duration}$ sin acceder internamente al motor TTS.

---

## 73. Contrato entre B-Roll y Editorial Planner

B-Roll Matcher deberá producir `BrollMatch[]`. El planner decidirá cómo incorporar esas selecciones al montaje final, permitiendo reemplazar el algoritmo de matching sin modificar el timeline engine.

---

## 74. Contrato de exportación

El exportador deberá recibir un `EditPlan` válido. Si el `EditPlan` es inválido:
$$\text{NO EXPORTAR} \longrightarrow \text{Emitir Error Estructurado}$$
Nunca deberá generar un JSX parcialmente inválido silenciosamente.

---

## 75. Contrato de recuperación

Los errores `RECOVERABLE` podrán producir resultados parciales únicamente si el contrato de la etapa lo permite. Un resultado parcial deberá identificarse explícitamente (`{ complete: false, warnings: [...] }`).

---

## 76. Tests obligatorios de contratos

Cada contrato deberá probar:
- [ ] instancia válida
- [ ] campo obligatorio ausente
- [ ] tipo incorrecto
- [ ] rango inferior
- [ ] rango superior
- [ ] timestamp inválido
- [ ] referencia inexistente
- [ ] enum inválido
- [ ] serialización
- [ ] deserialización
- [ ] round-trip
- [ ] determinismo

---

## 77. Property-Based Testing

Los contratos temporales deberán someterse a generación automática con propiedades mínimas:
$$\text{start} \ge 0, \quad \text{end} \ge \text{start}, \quad \text{duration} = \text{end} - \text{start}$$
$$-90 \le \text{latitude} \le 90, \quad -180 \le \text{longitude} \le 180$$
$$0 \le \text{score} \le 1$$

---

## 78. Golden Data

Se deberán crear fixtures canónicos para:
- `transcript`
- `audio analysis`
- `shot manifest`
- `classification`
- `B-Roll matching`
- `localization`
- `TTS`
- `EditPlan`
- `overlays`

---

## 79. Migraciones

Cuando cambie un schema ($v_1 \to v_2$), deberá existir una estrategia explícita de migración cuando sea necesario conservar artefactos existentes.

---

## 80. Regla de compatibilidad con v3.4.0

Los contratos existentes del motor no deberán modificarse directamente sólo para satisfacer la expansión:
$$\text{Existing Contract} \longrightarrow \text{Adapter} \longrightarrow \text{Vlog Contract}$$

---

## 81. Definition of Done

Este documento estará completo cuando:

- [ ] Todos los objetos principales están definidos
- [ ] Todas las unidades están definidas
- [ ] Todos los rangos están definidos
- [ ] IDs definidos
- [ ] Versionado definido
- [ ] Errores definidos
- [ ] Referencias definidas
- [ ] Reglas temporales definidas
- [ ] Serialización definida
- [ ] Hashing definido
- [ ] Localización definida
- [ ] TTS definido
- [ ] EditPlan definido
- [ ] GraphicsPlan definido
- [ ] Contracts Analysis → Editorial definidos
- [ ] Contracts Editorial → Export definidos
- [ ] Tests contractuales definidos
- [ ] Property tests definidos
- [ ] Golden fixtures definidos
- [ ] Migraciones contempladas

---

## 82. Estado del documento

**Documento:** `02-DATA-CONTRACTS.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

No deberá comenzar la implementación de los módulos dependientes hasta que los contratos correspondientes hayan sido aprobados.
