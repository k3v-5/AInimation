# Vlog Footage Classifier & A-Roll / B-Roll Matcher

**Documento:** `06-VLOG-FOOTAGE-CLASSIFIER.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog Multilingual Expansion  
**Dependencias:** Media Scanner, FFmpeg/decoder existente, LocalWhisperTranscriptionBridge, Timeline Engine, VlogJumpCutEngine, metadata pipeline, Semantic Matching Engine  

---

## 1. Objetivo

Definir un sistema completamente automatizable capaz de analizar una carpeta de material audiovisual y producir un inventario semántico y técnico de cada toma.

El sistema deberá clasificar automáticamente el material en:
- `A_ROLL`
- `B_ROLL`
- `TIMELAPSE`
- `ACTION`
- `UNKNOWN`

y posteriormente relacionar segmentos de B-roll con segmentos narrativos del A-roll.

El resultado deberá ser determinista, auditable y serializable.

---

## 2. Principio fundamental

El clasificador no podrá depender exclusivamente de:
- nombre del archivo;
- carpeta;
- fecha de creación;
- metadatos de cámara;
- duración;
- resolución.

Estos datos podrán utilizarse como señales auxiliares, nunca como única evidencia.

---

## 3. Arquitectura

```
Media Folder
     │
     ▼
Media Scanner
     │
     ▼
Technical Metadata Extractor
     │
     ▼
Shot Boundary Detector
     │
     ▼
Visual Feature Extractor
     │
     ▼
Audio Feature Extractor
     │
     ▼
Speech Detector
     │
     ▼
OCR / Text Detector
     │
     ▼
Motion Analyzer
     │
     ▼
Semantic Feature Extractor
     │
     ▼
Footage Classifier
     │
     ▼
Footage Index
     │
     ▼
Narrative Segment Analyzer
     │
     ▼
B-Roll Matcher
     │
     ▼
B-Roll Placement Plan
```

---

## 4. Componentes

`VlogFootageClassifier` se compone de:
- `MediaScanner`
- `MediaMetadataExtractor`
- `ShotSegmenter`
- `VisualFeatureExtractor`
- `MotionAnalyzer`
- `AudioFeatureExtractor`
- `SpeechPresenceDetector`
- `SceneSemanticAnalyzer`
- `FootageClassificationEngine`
- `FootageIndexer`
- `NarrativeSegmentAnalyzer`
- `BRollMatcher`
- `PlacementPlanner`
- `ClassificationValidator`

---

## 5. Input

```typescript
interface FootageClassificationInput {
  sourceDirectory: string;
  configuration: FootageClassifierConfig;
}
```

---

## 6. Output

```typescript
interface FootageClassificationResult {
  projectId: string;
  sourceDirectory: string;
  assets: ClassifiedFootageAsset[];
  index: FootageSemanticIndex;
  warnings: ClassificationWarning[];
  statistics: ClassificationStatistics;
}
```

---

## 7. Asset

```typescript
interface ClassifiedFootageAsset {
  id: string;
  path: string;
  sourceHash: string;
  metadata: MediaMetadata;
  segments: FootageSegment[];
}
```

---

## 8. Media Metadata

```typescript
interface MediaMetadata {
  duration: number;
  width: number;
  height: number;
  fps: number;
  codec?: string;
  container?: string;
  audioChannels?: number;
  sampleRate?: number;
  bitrate?: number;
}
```

---

## 9. Source Hash

Cada archivo deberá disponer de una identidad estable:
$$\text{sourceHash} = \text{SHA-256}(\text{file content})$$

El hash permitirá:
- detectar duplicados;
- detectar modificaciones;
- invalidar índices obsoletos;
- garantizar reproducibilidad.

---

## 10. Shot Segmentation

Un archivo podrá contener varias tomas. El clasificador no deberá asumir $1\text{ archivo} = 1\text{ toma}$. Deberá existir:

```typescript
interface FootageSegment {
  id: string;
  assetId: string;
  start: number;
  end: number;
  duration: number;
}
```

---

## 11. Segment Time Semantics

Todos los segmentos utilizarán:
$$[t_{\text{start}}, t_{\text{end}})$$

---

## 12. Segment Validity

Siempre:
$$\text{start} \ge 0, \quad \text{end} > \text{start}, \quad \text{end} \le \text{asset.duration}$$

---

## 13. Shot Boundary Detection

Las transiciones de toma podrán detectarse mediante:
- diferencia visual;
- histograma;
- cambio abrupto de movimiento;
- corte de cámara;
- cambio de exposición;
- cambio de escena.

El algoritmo concreto deberá ser intercambiable mediante una interfaz.

---

## 14. Shot Detector Interface

```typescript
interface ShotBoundaryDetector {
  detect(asset: MediaAsset): Promise<ShotBoundary[]>;
}
```

---

## 15. Boundary

```typescript
interface ShotBoundary {
  time: number;
  confidence: number;
  type: "CUT" | "FADE" | "DISSOLVE" | "UNKNOWN";
}
```

---

## 16. Visual Features

Cada segmento podrá contener:

```typescript
interface VisualFeatures {
  averageBrightness: number;
  colorHistogram: number[];
  motionScore: number;
  cameraMotionScore: number;
  faceCount: number;
  personCount: number;
  objectLabels: SemanticLabel[];
  sceneLabels: SemanticLabel[];
}
```

---

## 17. Normalización

Los scores deberán normalizarse a $0.0 \to 1.0$ salvo características explícitamente categóricas.

---

## 18. Audio Features

```typescript
interface AudioFeatures {
  speechProbability: number;
  musicProbability: number;
  environmentalAudioProbability: number;
  silenceRatio: number;
  rms: number;
  peak: number;
}
```

---

## 19. Speech Presence

El sistema deberá distinguir:
- `SPEECH`
- `NO_SPEECH`
- `MIXED`
- `UNKNOWN`

No deberá considerar automáticamente todo audio como diálogo.

---

## 20. Visual Face Detection

La presencia de una persona mirando a cámara será una señal importante para A-roll. Sin embargo:
$$\text{face detected} \ne \text{A\_ROLL}$$
Una toma de turistas o personas en una calle puede contener rostros y seguir siendo B-roll.

---

## 21. Face Features

```typescript
interface FaceFeature {
  count: number;
  largestFaceRatio: number;
  averageConfidence: number;
  frontalProbability: number;
  gazeToCameraProbability: number;
}
```

---

## 22. A-Roll Signals

Se considerarán señales positivas:
- voz clara;
- habla continua;
- rostro dominante;
- rostro frontal;
- mirada a cámara;
- encuadre de talking head;
- baja variación de escena.

---

## 23. B-Roll Signals

Se considerarán señales positivas:
- paisaje;
- comida;
- arquitectura;
- calles;
- objetos;
- monumentos;
- actividades;
- tomas de recurso;
- ausencia de voz;
- movimiento cinematográfico;
- múltiples planos ambientales.

---

## 24. Timelapse Signals

Se considerarán:
- velocidad visual anormalmente alta;
- cambios de iluminación acelerados;
- movimiento continuo de escena;
- duración de exposición temporal;
- ausencia de habla;
- patrones compatibles con timelapse.

---

## 25. Action Signals

Se considerarán:
- movimiento elevado;
- velocidad;
- cambios frecuentes de dirección;
- cámara dinámica;
- actividad física;
- deportes;
- conducción;
- POV;
- movimiento de objetos/personas.

---

## 26. Clasificación Multiseñal

La clasificación deberá utilizar múltiples features. Conceptualmente:
$$\text{score}(\text{class}) = \sum (\text{weight}_i \times \text{feature}_i)$$

---

## 27. Scores

```typescript
interface ClassificationScores {
  aRoll: number;
  bRoll: number;
  timelapse: number;
  action: number;
}
```
Todos deberán estar normalizados: $0 \le \text{score} \le 1$.

---

## 28. Confidence

La clasificación final deberá incluir:

```typescript
interface ClassificationResult {
  type: FootageType;
  confidence: number;
  scores: ClassificationScores;
  reasons: ClassificationReason[];
}
```

---

## 29. Confidence Threshold

Si ninguna categoría alcanza `classificationThreshold`:
$$\text{resultado} = \text{UNKNOWN}$$
No deberá forzarse una clasificación.

---

## 30. Ambiguous Classification

Si dos categorías presentan scores prácticamente iguales (ej. $\text{A\_ROLL} = 0.78, \text{B\_ROLL} = 0.77$), el sistema deberá registrar ambigüedad. Valor recomendado inicial: usar mayor score + warning de ambigüedad.

---

## 31. Classification Reason

```typescript
interface ClassificationReason {
  feature: string;
  contribution: number;
  explanation: string;
}
```
Esto permitirá auditoría total.

---

## 32. Ejemplo

```json
{
  "type": "A_ROLL",
  "confidence": 0.93,
  "reasons": [
    {
      "feature": "speechProbability",
      "contribution": 0.31,
      "explanation": "Continuous speech detected"
    },
    {
      "feature": "frontalProbability",
      "contribution": 0.24,
      "explanation": "Primary frontal face detected"
    }
  ]
}
```

---

## 33. Configuración

```typescript
interface FootageClassifierConfig {
  classificationThreshold: number;
  ambiguityMargin: number;
  shotDetectionSensitivity: number;
  enableOCR: boolean;
  enableFaceDetection: boolean;
  enableObjectDetection: boolean;
  enableSemanticAnalysis: boolean;
  enableAudioAnalysis: boolean;
}
```

---

## 34. OCR

Cuando exista texto visual relevante (`hotel`, `centro histórico`, `Guadalajara`, `restaurant`, `airport`), podrá incorporarse como metadata semántica. OCR no será obligatorio para clasificar A/B-roll.

---

## 35. Semantic Labels

```typescript
interface SemanticLabel {
  label: string;
  confidence: number;
  source: "VISION" | "OCR" | "AUDIO" | "METADATA";
}
```

---

## 36. Semantic Vocabulary

El sistema deberá utilizar un vocabulario normalizado:
- `restaurant`, `food`, `street`, `city`, `museum`, `hotel`, `airport`, `beach`, `mountain`, `car`, `train`, `bus`, `landmark`, `person`, `building`, `nature`.

---

## 37. Synonym Normalization

Conceptos equivalentes deberán normalizarse:
$$\text{"restaurante"}, \text{"restaurant"}, \text{"restaurante mexicano"}, \text{"eatery"} \implies \text{restaurant}$$
El diccionario deberá ser versionado.

---

## 38. Multilingual Labels

El índice deberá ser independiente del idioma de la narración:
$$\text{"restaurante"}, \text{"restaurant"} \implies \text{PLACE\_RESTAURANT}$$

---

## 39. Canonical Semantic IDs

Se recomienda:
- `PLACE_RESTAURANT`
- `PLACE_HOTEL`
- `PLACE_AIRPORT`
- `PLACE_MUSEUM`
- `PLACE_BEACH`
- `PLACE_CITY_CENTER`
- `FOOD`
- `LANDMARK`
- `TRANSPORT`
- `NATURE`
- `PEOPLE`
- `ACTIVITY`

---

## 40. Semantic Index

```typescript
interface FootageSemanticIndex {
  entries: SemanticIndexEntry[];
}
```

---

## 41. Index Entry

```typescript
interface SemanticIndexEntry {
  segmentId: string;
  labels: SemanticLabel[];
  embedding?: number[];
  keywords: string[];
}
```

---

## 42. Embeddings

El sistema podrá soportar embeddings locales. No se deberá exigir una API externa:

```typescript
interface LocalEmbeddingProvider {
  embed(text: string): Promise<number[]>;
}
```

---

## 43. Offline Requirement

El clasificador deberá poder funcionar sin servicios externos. Cualquier modelo opcional deberá ser local.

---

## 44. Narrative Segment

Para realizar matching se analizará el A-roll:

```typescript
interface NarrativeSegment {
  id: string;
  start: number;
  end: number;
  text: string;
  language: string;
  keywords: string[];
  semanticLabels: string[];
  importanceScore: number;
}
```

---

## 45. Narrative Extraction

Los segmentos narrativos podrán provenir de:
- Whisper;
- transcript existente;
- capítulos;
- markers;
- segmentación semántica.

---

## 46. Word Alignment

Cuando exista timestamp por palabra:

```typescript
interface WordTimestamp {
  word: string;
  start: number;
  end: number;
  confidence: number;
}
```
deberá conservarse.

---

## 47. Narrative Segmentation

No deberá utilizarse únicamente una ventana temporal fija. La segmentación podrá considerar:
- oración;
- cambio de tema;
- entidad mencionada;
- pausa;
- énfasis;
- cambio de escena.

---

## 48. Narrative Topic

```typescript
interface NarrativeTopic {
  id: string;
  label: string;
  confidence: number;
}
```

---

## 49. Matching

El B-roll matcher deberá calcular:
$$\text{matchScore} = \text{semanticSimilarity} + \text{keywordSimilarity} + \text{temporalCompatibility} + \text{visualQuality} + \text{coverage} - \text{repetitionPenalty}$$

---

## 50. Match Result

```typescript
interface BRollMatch {
  narrativeSegmentId: string;
  footageSegmentId: string;
  score: number;
  reasons: MatchReason[];
}
```

---

## 51. Semantic Similarity

Ejemplo:
- Narración: *"Fuimos al centro histórico"*
- B-roll labels: `CITY`, `LANDMARK`, `HISTORIC_BUILDING`
- Recibe un score alto.

---

## 52. Keyword Similarity

Las palabras explícitas deberán tener peso elevado. Ejemplo: *"Hotel Reforma"* $\leftrightarrow$ toma etiquetada `HOTEL_REFORMA` superará a una toma genérica de hotel.

---

## 53. Temporal Compatibility

El B-roll no necesariamente tiene que existir exactamente cuando se menciona. El matcher deberá permitir:
- `pre-roll`
- `synchronous`
- `post-roll`

---

## 54. Pre-Roll

Una toma podrá comenzar antes de la frase relevante.

---

## 55. Synchronous

Una toma podrá comenzar durante la frase relevante.

---

## 56. Post-Roll

Una toma podrá continuar después de la frase relevante.

---

## 57. Default Coverage

La configuración inicial deberá permitir:
$$\text{startOffset} = -0.50\text{ s}, \quad \text{endOffset} = +0.75\text{ s}$$
Estos valores deberán ser configurables.

---

## 58. Minimum B-Roll Duration

No se deberá insertar una toma demasiado corta. `minimumBRollDuration` será configurable.

---

## 59. Maximum B-Roll Duration

También existirá `maximumBRollDuration` para evitar tomas eternas.

---

## 60. B-Roll Loop

Si una toma es demasiado corta para cubrir el espacio solicitado:
$$\text{NO LOOP (por defecto)}$$
Deberá buscarse otra toma.

---

## 61. B-Roll Trimming

Una toma suficientemente larga podrá recortarse (`sourceStart`, `sourceEnd`) sin alterar el archivo original.

---

## 62. B-Roll Selection

El matcher deberá seleccionar el mejor candidato disponible. Si el candidato principal ya fue utilizado recientemente, deberá aplicarse penalización.

---

## 63. Repetition Penalty

El mismo clip no deberá repetirse continuamente. `repetitionPenalty` será configurable.

---

## 64. Diversity

El sistema deberá favorecer:
- diferentes clips;
- diferentes ángulos;
- diferentes distancias;
- diferentes movimientos.

---

## 65. Coverage

El matcher deberá evitar dejar segmentos narrativos importantes sin B-roll cuando exista material compatible.

---

## 66. Coverage Score

```typescript
interface CoverageResult {
  narrativeSegmentId: string;
  covered: boolean;
  coverageRatio: number;
}
```

---

## 67. No Suitable B-Roll

Si no existe material adecuado:
$$\text{KEEP\_A\_ROLL}$$
Nunca deberá insertar un clip semánticamente incorrecto únicamente para rellenar.

---

## 68. Confidence Threshold

Si $\text{bestMatchScore} < \text{matchThreshold}$:
$$\text{resultado} = \text{NO\_MATCH}$$

---

## 69. Placement Plan

```typescript
interface BRollPlacement {
  id: string;
  narrativeSegmentId: string;
  footageSegmentId: string;
  sourceStart: number;
  sourceEnd: number;
  outputStart: number;
  outputEnd: number;
  score: number;
}
```

---

## 70. Layer Priority

El plan deberá declarar prioridad:
$$\text{A\_ROLL} \longrightarrow \text{B\_ROLL} \longrightarrow \text{OVERLAY} \longrightarrow \text{SFX}$$

---

## 71. B-Roll Visual Replacement

Por defecto:
$$\text{B-roll} = \text{overlay sobre A-roll}$$
No deberá eliminarse la pista de voz.

---

## 72. Audio Policy

El audio original del B-roll podrá configurarse como: `MUTE`, `DUCK`, `KEEP`. Valor inicial recomendado: `DUCK`.

---

## 73. Ducking

Cuando exista narración:
$$\text{B-roll audio} \longrightarrow -12\text{ dB (configurable)}$$
La cifra exacta pertenecerá a la configuración de Audio Engine.

---

## 74. B-Roll Transition

Por defecto: `CUT`. El estilo podrá sustituirlo posteriormente.

---

## 75. Style Independence

El clasificador no decidirá `whip pan`, `glitch`, `flash` o `crossfade`; eso corresponde al Style Engine.

---

## 76. Cinematic B-Roll

El índice deberá registrar atributos que posteriormente puedan utilizar los estilos:
- `cameraMotion`
- `brightness`
- `dominantColor`
- `shotScale`

---

## 77. Shot Scale

Opcionalmente:
- `EXTREME_CLOSE_UP`
- `CLOSE_UP`
- `MEDIUM`
- `WIDE`
- `EXTREME_WIDE`
- `UNKNOWN`

---

## 78. Camera Movement

- `STATIC`
- `PAN`
- `TILT`
- `DOLLY`
- `HANDHELD`
- `GIMBAL`
- `ZOOM`
- `UNKNOWN`

---

## 79. Quality Score

Cada segmento podrá recibir `qualityScore: number` considerando:
- exposición;
- estabilidad;
- nitidez;
- clipping;
- ruido;
- duración útil.

---

## 80. Quality Guard

Un clip de baja calidad no deberá ganar únicamente por coincidencia semántica. El ranking deberá incluir:
$$\text{semantic relevance} + \text{technical quality}$$

---

## 81. Duplicate Detection

El índice deberá detectar:
- archivos duplicados;
- clips prácticamente idénticos;
- segmentos repetidos.

---

## 82. Duplicate Policy

Los duplicados no deberán utilizarse como clips independientes salvo configuración explícita.

---

## 83. Determinismo

Para la misma:
$$\text{sourceHash} + \text{configurationVersion} + \text{modelVersion}$$
el resultado deberá ser idéntico.

---

## 84. Model Version

Todo modelo local utilizado deberá registrar:
- `modelName`
- `modelVersion`
- `modelChecksum`

---

## 85. Cache

Los features costosos deberán almacenarse en caché. Clave mínima:
$$\text{sourceHash} + \text{modelChecksum} + \text{featureVersion}$$

---

## 86. Cache Invalidation

Cambiar cualquiera de los anteriores deberá invalidar el resultado correspondiente.

---

## 87. Processing Pipeline

Orden obligatorio:
1. Scan
2. Hash
3. Metadata
4. Shot segmentation
5. Feature extraction
6. Classification
7. Semantic indexing
8. Narrative analysis
9. Matching
10. Placement
11. Validation
12. Serialization

---

## 88. Parallel Processing

Los assets independientes podrán analizarse en paralelo. La salida final deberá ordenarse de manera determinista.

---

## 89. Resource Limits

La configuración deberá soportar:
- `maxConcurrentAssets`
- `maxMemoryMB`
- `maxProcessingTime`

---

## 90. Failure Isolation

Si un archivo está corrupto: $\text{asset status} = \text{ERROR}$, pero el resto del proyecto deberá continuar cuando sea seguro.

---

## 91. Error Model

```typescript
interface ClassificationError {
  assetId?: string;
  code: string;
  message: string;
  fatal: boolean;
}
```

---

## 92. Errores mínimos

- `MEDIA_NOT_FOUND`
- `MEDIA_UNREADABLE`
- `INVALID_DURATION`
- `INVALID_FPS`
- `DECODER_ERROR`
- `FEATURE_EXTRACTION_ERROR`
- `MODEL_ERROR`
- `INDEX_ERROR`
- `MATCHING_ERROR`

---

## 93. Warnings

Ejemplos:
- `LOW_CLASSIFICATION_CONFIDENCE`
- `AMBIGUOUS_CLASSIFICATION`
- `NO_BROLL_MATCH`
- `LOW_VISUAL_QUALITY`
- `DUPLICATE_ASSET`
- `MISSING_AUDIO`
- `MISSING_FACES`

---

## 94. Statistics

```typescript
interface ClassificationStatistics {
  totalAssets: number;
  totalSegments: number;
  aRollCount: number;
  bRollCount: number;
  timelapseCount: number;
  actionCount: number;
  unknownCount: number;
  matchedNarrativeSegments: number;
  unmatchedNarrativeSegments: number;
}
```

---

## 95. JSON Artifact

El sistema deberá producir:
- `footage-index.json`
- `broll-placement-plan.json`

---

## 96. Footage Index

El índice deberá poder reutilizarse en futuras ejecuciones sin volver a analizar los archivos que no hayan cambiado.

---

## 97. Placement Plan

El placement plan deberá poder consumirse directamente por el `Timeline Engine` sin depender del clasificador.

---

## 98. Separación de responsabilidades

$$\text{Classifier} \longrightarrow \text{Index}$$
$$\text{Matcher} \longrightarrow \text{Placement Plan}$$
$$\text{Timeline Engine} \longrightarrow \text{Timeline}$$
$$\text{After Effects Exporter} \longrightarrow \text{JSX}$$

---

## 99. Test — A-Roll

Material: rostro frontal, voz continua, fondo estable.  
Esperado: `A_ROLL` con alta confianza.

---

## 100. Test — B-Roll

Material: plaza, sin voz, movimiento suave.  
Esperado: `B_ROLL`.

---

## 101. Test — Timelapse

Material: nubes aceleradas, cambio rápido de luz, sin voz.  
Esperado: `TIMELAPSE`.

---

## 102. Test — Action

Material: bicicleta, POV, movimiento elevado.  
Esperado: `ACTION`.

---

## 103. Test — Unknown

Material ambiguo y baja confianza.  
Esperado: `UNKNOWN` o categoría dominante + warning según configuración.

---

## 104. Test — Semantic Match

Narración: *"Después fuimos al restaurante"*.  
Clip: `labels = [FOOD, PLACE_RESTAURANT]`.  
Esperado: $\text{matchScore} \ge \text{threshold}$.

---

## 105. Test — Bad Semantic Match

Narración: *"Visitamos el museo"*.  
Clip: `labels = [BEACH]`.  
Esperado: `NO_MATCH`.

---

## 106. Test — Multilingual Match

Narración: *"Fuimos al restaurante"* y *"We went to the restaurant"* deberán recuperar esencialmente el mismo conjunto de clips.

---

## 107. Test — Repetition

Si existen `clip A`, `clip B`, `clip C`, el matcher deberá evitar `A, A, A, A` si existen alternativas suficientemente buenas.

---

## 108. Test — No B-Roll

Si ningún clip supera el threshold: `NO_MATCH` y `KEEP_A_ROLL`.

---

## 109. Test — Corrupt Asset

Un archivo ilegible no deberá detener el procesamiento de assets válidos.

---

## 110. Test — Duplicate

Dos archivos con idéntico hash deberán detectarse como duplicados.

---

## 111. Property-Based Testing

Generar aleatoriamente $N$ assets, $N$ segments, $N$ labels, $N$ narrative segments y comprobar:
$$\text{scores} \in [0, 1], \quad \text{confidence} \in [0, 1], \quad \text{durations} > 0$$
placements válidos y ausencia de referencias rotas.

---

## 112. Matching Invariants

Todo placement deberá apuntar a:
- `existing narrativeSegmentId`
- `existing footageSegmentId`

---

## 113. Temporal Invariants

Todo placement deberá cumplir:
$$\text{sourceStart} < \text{sourceEnd}, \quad \text{outputStart} < \text{outputEnd}$$

---

## 114. Referential Integrity

No deberá existir:
- `placement` $\longrightarrow$ `missing asset`
- `placement` $\longrightarrow$ `missing segment`

---

## 115. Performance

El sistema deberá evitar extraer features repetidamente. La caché deberá ser utilizada siempre que los inputs sean idénticos.

---

## 116. Incremental Processing

Modificar un único archivo deberá invalidar únicamente el asset y sus placements dependientes, no todo el proyecto.

---

## 117. Auditability

Cada clasificación deberá poder explicar qué decidió, por qué, con qué features, modelo y configuración.

---

## 118. Reproducibility

El artefacto deberá registrar:
- `engineVersion`
- `classifierVersion`
- `modelVersion`
- `configurationVersion`
- `sourceHash`
- `createdAt`

---

## 119. No External API Requirement

El pipeline completo deberá poder ejecutarse:
- offline
- sin API keys
- sin servicios cloud
- sin coste por minuto

---

## 120. Optional Models

Los modelos externos podrán existir únicamente como extensiones; la arquitectura base no deberá depender de ellos.

---

## 121. Security

Los paths deberán validarse. No deberá permitirse que metadata de un archivo se convierta directamente en comandos shell sin sanitización.

---

## 122. Path Safety

El sistema deberá tratar los paths como datos. Nunca ejecutar comandos concatenados de shell sin escaping seguro.

---

## 123. Export Compatibility

El placement plan deberá ser compatible con:
- 16:9
- 9:16
- 1:1
- 4:5
- 21:9
sin alterar la clasificación semántica.

---

## 124. Style Compatibility

El índice no deberá contener decisiones específicas de estilos (`MrBeast`, `Hormozi`, `TIME`, `Vox`); consumirá atributos neutrales.

---

## 125. Future Extension

La arquitectura deberá permitir categorías futuras:
- `SCREEN_RECORDING`
- `DRONE`
- `UNDERWATER`
- `INTERVIEW`
- `PRODUCT_SHOT`
- `POV`
sin modificar el contrato principal.

---

## 126. Definition of Done

- [ ] Media scanning definido
- [ ] Hashing definido
- [ ] Metadata definido
- [ ] Shot segmentation definido
- [ ] Visual features definido
- [ ] Audio features definido
- [ ] Face features definido
- [ ] Motion analysis definido
- [ ] OCR definido
- [ ] Semantic labels definido
- [ ] Classification scoring definido
- [ ] Confidence definido
- [ ] UNKNOWN definido
- [ ] Semantic index definido
- [ ] Narrative segmentation definido
- [ ] B-roll matching definido
- [ ] Temporal compatibility definido
- [ ] Repetition policy definida
- [ ] Quality scoring definido
- [ ] Placement plan definido
- [ ] Cache definido
- [ ] Incremental processing definido
- [ ] Error model definido
- [ ] Determinism definido
- [ ] Offline requirement definido
- [ ] Tests unitarios definidos
- [ ] Property tests definidos
- [ ] Fuzz tests definidos
- [ ] Performance definido
- [ ] Serialization definida
- [ ] Integración Timeline definida
- [ ] Integración AE definida

---

## 127. Estado del documento

**Documento:** `06-VLOG-FOOTAGE-CLASSIFIER.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

Este documento establece el contrato técnico completo para convertir material crudo en un índice audiovisual semántico y un plan automatizado de utilización de B-roll. La implementación deberá respetar este contrato y no introducir comportamiento implícito que no esté documentado.
