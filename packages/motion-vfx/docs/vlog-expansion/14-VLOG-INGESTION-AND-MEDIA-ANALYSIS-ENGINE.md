# Vlog Ingestion & Media Analysis Engine

**Documento:** `14-VLOG-INGESTION-AND-MEDIA-ANALYSIS-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  
**Dependencias:** Documento 13 — Vlog Project Schema & Declarative Production DSL  

---

## 1. Objetivo

Definir completamente el comportamiento del subsistema responsable de recibir material audiovisual bruto y convertirlo en un inventario técnico y semántico listo para las etapas posteriores.

El módulo deberá:
- descubrir archivos;
- identificar formatos;
- validar archivos;
- calcular hashes;
- extraer metadatos;
- detectar streams;
- analizar video;
- analizar audio;
- detectar habla;
- detectar silencios;
- detectar movimiento;
- detectar posibles rostros;
- detectar orientación;
- detectar duplicados;
- construir proxies cuando corresponda;
- generar thumbnails;
- registrar errores;
- producir resultados deterministas;
- preservar absolutamente los archivos originales.

---

## 2. Principio Fundamental

El sistema deberá tratar los archivos originales como `READ-ONLY`.

Nunca deberá:
- sobrescribir;
- renombrar;
- mover;
- recodificar;
- recortar;
- modificar metadata;
- alterar timestamps del filesystem;
- eliminar;
- sustituir;
ningún archivo perteneciente al directorio de entrada.

---

## 3. Flujo General

```
INPUT DIRECTORY
      │
      ▼
DISCOVERY
      │
      ▼
FILE VALIDATION
      │
      ▼
HASHING
      │
      ▼
MEDIA PROBE
      │
      ├──────────────┐
      ▼              ▼
VIDEO ANALYSIS    AUDIO ANALYSIS
      │              │
      └──────┬───────┘
             ▼
      SEMANTIC ANALYSIS
             │
             ▼
      ASSET REGISTRY
             │
             ▼
      INGESTION REPORT
             │
             ▼
      NEXT PIPELINE STAGE
```

---

## 4. Input Contract

```typescript
interface IngestionInput {
  inputDirectory: string;
  projectDirectory: string;
  configuration: IngestionConfig;
}
```

---

## 5. Input Directory

La carpeta de entrada podrá contener videos, audio, imágenes, subdirectorios, exportaciones de cámara, grabaciones de teléfono o capturas de pantalla. El sistema procesará recursivamente los subdirectorios salvo configuración en contra.

---

## 6. Supported Video Containers

Formatos soportados por herramientas locales configuradas (prioridad: MP4, MOV, M4V, MKV, AVI, WEBM, MXF). El soporte efectivo se detecta mediante probing; la extensión no garantiza el codec.

---

## 7. Supported Audio Containers

Mínimo: WAV, MP3, M4A, AAC, FLAC, OGG, OPUS.

---

## 8. Supported Images

Mínimo: PNG, JPG/JPEG, WEBP, TIFF, BMP.

---

## 9. Unsupported Files

Los archivos desconocidos deberán registrarse y marcarse como `UNSUPPORTED` sin bloquear el procesamiento del resto.

---

## 10. Hidden Files

Por defecto deberán ignorarse archivos ocultos del sistema (`.DS_Store`, `Thumbs.db`, `desktop.ini`).

---

## 11. Temporary Files

Deberán ignorarse patrones temporales (`*.tmp`, `*.part`, `*.crdownload`, `*.download`).

---

## 12. Symlinks

Comportamiento configurable:

```typescript
type SymlinkPolicy =
  | "IGNORE"
  | "FOLLOW_SAFE"
  | "FOLLOW_ALL";
```
Por defecto: `IGNORE`.

---

## 13. Path Security

Todo path deberá normalizarse para impedir escapes del directorio raíz autorizado (Path Traversal).

---

## 14. File Identity

```typescript
interface FileIdentity {
  absolutePath: string;
  relativePath: string;
  filename: string;
  extension: string;
  sizeBytes: number;
}
```

---

## 15. File Hash

Cálculo de hash criptográfico sobre los bytes reales del archivo:

```typescript
interface FileHash {
  algorithm: "sha256";
  value: string;
}
```

---

## 16. Hash Integrity

El hash se calcula estrictamente sobre el contenido binario del archivo, nunca sobre nombres, fechas o tamaños.

---

## 17. Duplicate Detection

Dos archivos con idéntico SHA-256 se consideran contenido duplicado.

---

## 18. Duplicate Policy

El sistema no eliminará duplicados; registrará su agrupación lógica:

```typescript
interface DuplicateGroup {
  hash: string;
  assetIds: string[];
}
```

---

## 19. Asset ID

El Asset ID deberá ser estable e independiente del orden de descubrimiento en el filesystem.

---

## 20. Recommended Asset ID

$$\text{asset\_<short-hash>} \quad (\text{ejemplo: } \text{asset\_8f31c2d9})$$

---

## 21. Media Probe

```typescript
interface MediaProbe {
  container?: string;
  formatName?: string;
  duration?: number;
  bitrate?: number;
  streams: MediaStream[];
}
```

---

## 22. Media Stream

```typescript
interface MediaStream {
  index: number;
  type: "VIDEO" | "AUDIO" | "SUBTITLE" | "DATA" | "UNKNOWN";
  codec?: string;
  codecName?: string;
}
```

---

## 23. Video Stream Metadata

```typescript
interface VideoStreamMetadata {
  width: number;
  height: number;
  fps: number;
  codec: string;
  pixelFormat?: string;
  colorSpace?: string;
  colorRange?: string;
  duration: number;
  rotation?: number;
}
```

---

## 24. FPS

Diferenciar entre FPS nominal, FPS promedio, base temporal, frame rate constante (CFR) y variable (VFR).

---

## 25. VFR Detection

```typescript
frameRateMode:
  | "CFR"
  | "VFR"
  | "UNKNOWN";
```

---

## 26. VFR Policy

El motor no convertirá silenciosamente VFR a CFR durante la ingestión; cualquier normalización se realizará en etapas explícitas posteriores.

---

## 27. Resolution

Preservación de resolución nativa (3840×2160, 1920×1080, 1080×1920, 1440×1080, 1280×720).

---

## 28. Rotation Metadata

Interpretación de flags de rotación de cámara, diferenciando dimensiones físicas de dimensiones de visualización.

---

## 29. Orientation

```typescript
type Orientation =
  | "LANDSCAPE"
  | "PORTRAIT"
  | "SQUARE";
```

---

## 30. Aspect Ratio

Calculado desde las dimensiones reales de presentación.

---

## 31. Video Duration

Precisión en punto flotante para evitar errores en límites de fotograma (prohibido redondear a enteros).

---

## 32. Audio Stream Detection

Registro de presencia de audio, cantidad de pistas, frecuencia de muestreo, canales, codec y duración.

---

## 33. Multiple Audio Streams

Conservación independiente de cada stream de audio (`audioStream[0]`, `audioStream[1]`, etc.).

---

## 34. Audio Channel Layout

Registro de `mono`, `stereo`, `5.1`, `7.1` o `unknown`.

---

## 35. Sample Rate

Preservación del sample rate original (44100, 48000, 96000 Hz).

---

## 36. Audio Loudness

```typescript
interface LoudnessAnalysis {
  rmsDb?: number;
  peakDb?: number;
  loudnessIntegrated?: number;
  dynamicRange?: number;
}
```

---

## 37. Audio Clipping

```typescript
interface ClippingAnalysis {
  detected: boolean;
  peakCount?: number;
}
```

---

## 38. Speech Detection

```typescript
interface SpeechAnalysis {
  detected: boolean;
  regions: SpeechRegion[];
  confidence?: number;
}
```

---

## 39. Speech Region

```typescript
interface SpeechRegion {
  start: number;
  end: number;
  confidence?: number;
}
```

---

## 40. Silence Detection

```typescript
interface SilenceRegion {
  start: number;
  end: number;
  duration: number;
  confidence?: number;
}
```

---

## 41. Silence Threshold

Umbral configurable ($250\text{ ms}$ por defecto para Vlog). La ingestión únicamente identifica los silencios, no los elimina.

---

## 42. Micro-Silences

Conservación analítica de micro-silencios inferiores al umbral.

---

## 43. Breathing Detection

```typescript
interface BreathRegion {
  start: number;
  end: number;
  confidence: number;
}
```

---

## 44. Breathing ≠ Silence

Una respiración audible no debe etiquetarse ciegamente como silencio eliminable.

---

## 45. Voice Activity Detection

```typescript
interface VADProvider {
  detect(audio: AudioInput): Promise<SpeechRegion[]>;
}
```

---

## 46. Offline Requirement

El módulo VAD debe operar 100% offline.

---

## 47. Transcription Handoff

La ingestión no transcribe texto; prepara los artefactos normalizados requeridos por el módulo de transcripción.

---

## 48. Whisper Preparation

Generación de referencia de audio normalizado, duración y regiones de habla para Whisper.

---

## 49. Frame Sampling

```typescript
interface SamplingConfig {
  intervalSeconds?: number;
  maxFrames?: number;
}
```

---

## 50. No Full Decode by Default

Prohibido decodificar el vídeo completo para el análisis preliminar de metadatos.

---

## 51. Thumbnail Generation

```typescript
interface Thumbnail {
  timestamp: number;
  path: string;
}
```

---

## 52. Thumbnail Strategy

Muestreo por defecto: inicio, $25\%$, $50\%$, $75\%$ y final.

---

## 53. Contact Sheet

Generación de hojas de contacto (`asset_contact_sheet.jpg`).

---

## 54. Contact Sheet Metadata

Vinculación estricta de cada miniatura con `assetId` y `timestamp`.

---

## 55. Scene Boundary Detection

```typescript
interface ShotBoundary {
  timestamp: number;
  confidence: number;
}
```

---

## 56. Shot Detection

Detección mediante diferencia de histogramas, diferencia estructural o detector local intercambiable.

---

## 57. Camera Motion

```typescript
interface MotionAnalysis {
  averageMotion: number;
  cameraMotion?: number;
  staticScore?: number;
}
```

---

## 58. Motion Classification

Clasificación: `STATIC`, `LOW`, `MEDIUM`, `HIGH`, `EXTREME`.

---

## 59. Blur Detection

```typescript
interface SharpnessAnalysis {
  score: number;
  blurry: boolean;
}
```

---

## 60. Exposure Analysis

```typescript
interface ExposureAnalysis {
  averageLuma: number;
  underexposedScore: number;
  overexposedScore: number;
}
```

---

## 61. Quality Score

Puntuación técnica normalizada:
$$\text{qualityScore} \in [0, 100]$$

---

## 62. Quality Score Components

Ponderación configurable de nitidez, exposición, calidad de audio, estabilidad y resolución.

---

## 63. Face Detection

```typescript
interface FaceRegion {
  x: number;
  y: number;
  width: number;
  height: number;
  confidence: number;
}
```

---

## 64. Face Tracking

```typescript
interface FaceTrack {
  id: string;
  regions: TimedFaceRegion[];
}
```

---

## 65. Eye Anchor

```typescript
interface EyeAnchor {
  x: number;
  y: number;
  confidence: number;
}
```

---

## 66. Active Speaker Candidate

Candidato A-Roll ante concurrencia de habla clara, rostro dominante y encuadre frontal.

---

## 67. A-Roll Score

```typescript
interface ARollScore {
  speechScore: number;
  faceScore: number;
  framingScore: number;
  finalScore: number;
}
```

---

## 68. B-Roll Candidate

Candidato B-Roll ante bajo diálogo directo, riqueza visual y duración útil.

---

## 69. Action Candidate

Material con elevado vector de movimiento y desplazamientos dinámicos de cámara.

---

## 70. Timelapse Candidate

Indicadores de progresión temporal acelerada e iluminación de frecuencia anormal.

---

## 71. Location Metadata

Extracción de geolocalización desde EXIF, metadatos del contenedor o estructura de carpetas.

---

## 72. No Fabricated Location

Si no hay evidencia técnica suficiente: $\text{location} = \text{null}$; prohibido inventar datos geográficos.

---

## 73. Date Metadata

Conservación independiente de fecha de creación del medio y fecha del filesystem.

---

## 74. Metadata Trust

```typescript
type MetadataSource =
  | "EXIF"
  | "CONTAINER"
  | "FILENAME"
  | "FOLDER"
  | "USER"
  | "UNKNOWN";
```

---

## 75. Filename Semantic Parsing

Análisis heurístico de nombres (`Guadalajara_Centro_001.MP4`) con índice de confianza asociado.

---

## 76. Filename Confidence

Toda inferencia por nombre de archivo es tratada como señal probabilística.

---

## 77. Folder Semantic Parsing

Inferencia de contexto geográfico o temático a partir de carpetas contenedoras (`/raw/Guadalajara/Centro/`).

---

## 78. Camera Metadata

Extracción de fabricante, modelo, óptica, ISO, obturación y apertura cuando esté disponible en EXIF.

---

## 79. GPS

Almacenamiento de coordenadas sin modificar los metadatos del archivo original.

---

## 80. Privacy Mode

Opción `privacyMode: boolean` para anonimizar o excluir coordenadas de los reportes públicos.

---

## 81. Original Metadata Preservation

Referencia inmutable al archivo de origen y creación de snapshots de metadatos independientes.

---

## 82. Proxy Generation

Generación opcional de proxies (`proxyEnabled: boolean`).

---

## 83. Proxy Purpose

Uso exclusivo para previsualización rápida, scrub eficiente y análisis de bajo consumo de memoria.

---

## 84. Proxy Isolation

Los proxies nunca sustituyen al asset maestro original en el registro del proyecto.

---

## 85. Proxy Metadata

```typescript
interface ProxyAsset {
  assetId: string;
  proxyPath: string;
  width: number;
  height: number;
  fps: number;
}
```

---

## 86. Waveform Generation

Generación de representaciones vectoriales de forma de onda (`waveform.json`).

---

## 87. Audio Feature Cache

Caché persistente de RMS, picos, silencios, habla y respiraciones.

---

## 88. Visual Feature Cache

Caché persistente de miniaturas, tomas, rostros, movimiento y nitidez.

---

## 89. Analysis Version

```typescript
interface AnalysisVersion {
  analyzer: string;
  version: string;
}
```

---

## 90. Deterministic Analysis

$$\text{Mismo input} + \text{Misma config} + \text{Misma versión de analizador} \implies \text{Idéntico resultado}$$

---

## 91. Randomness

Semilla explícita (`seed: number`) en cualquier algoritmo con componente estocástico.

---

## 92. Analysis Manifest

Cada activo produce su manifiesto individual `asset-analysis.json`.

---

## 93. Example Analysis Structure

```json
{
  "assetId": "asset_8f31c2d9",
  "hash": {
    "algorithm": "sha256",
    "value": "..."
  },
  "media": {
    "duration": 42.18,
    "width": 3840,
    "height": 2160,
    "fps": 29.97
  },
  "audio": {
    "hasAudio": true
  },
  "speech": {
    "detected": true
  },
  "quality": {
    "score": 91
  }
}
```

---

## 94. Ingestion Manifest

Generación del catálogo unificado `ingestion-manifest.json` con todos los activos descubiertos.

---

## 95. Ingestion Report

Emisión del informe `ingestion-report.json` detallando procesados, omitidos, no soportados, duplicados y advertencias.

---

## 96. Error Classification

```typescript
type IngestionErrorCode =
  | "FILE_NOT_FOUND"
  | "PERMISSION_DENIED"
  | "CORRUPT_MEDIA"
  | "UNSUPPORTED_FORMAT"
  | "PROBE_FAILED"
  | "HASH_FAILED"
  | "ANALYSIS_FAILED"
  | "INVALID_METADATA"
  | "UNKNOWN";
```

---

## 97. Error Isolation

Un archivo corrupto o ilegible no interrumpe el procesamiento del resto de los activos válidos.

---

## 98. Fatal Errors

Detención total únicamente ante violaciones de seguridad, paths de proyecto inválidos o fallos de escritura de manifiestos.

---

## 99. Warning vs Error

Las advertencias no bloquean el pipeline; los errores en activos requeridos detienen etapas específicas.

---

## 100. Progress Reporting

```typescript
interface IngestionProgress {
  discovered: number;
  processed: number;
  failed: number;
  currentAsset?: string;
  percent: number;
}
```

---

## 101. Cancellation

Cancelación limpia marcando los artefactos parciales como incompletos.

---

## 102. Resume

Reanudación inteligente de sesiones interrumpidas reutilizando hashes y manifiestos previos.

---

## 103. Idempotency

Ejecutar la ingestión dos veces sobre el mismo material reutiliza análisis válidos sin reprocesar.

---

## 104. Changed File

Modificar el hash de un archivo invalida su identidad y genera una nueva revisión.

---

## 105. Asset Revision

```typescript
interface AssetRevision {
  assetId: string;
  revision: number;
  hash: string;
}
```

---

## 106. File Renaming

Renombrar un archivo conservando idéntico hash no genera un activo nuevo.

---

## 107. File Movement

Mover un archivo dentro de la raíz de entrada preserva su identidad lógica si su hash es idéntico.

---

## 108. Missing Asset

Si un archivo desaparece, su registro se conserva marcado como `MISSING`.

---

## 109. No Silent Replacement

Un archivo con distinto contenido jamás sustituye silenciosamente a un activo previo con igual nombre.

---

## 110. Analysis Dependency Graph

```
HASH
 │
 ▼
PROBE
 ├── VIDEO ANALYSIS
 │     ├── THUMBNAILS
 │     ├── SHOTS
 │     ├── MOTION
 │     ├── QUALITY
 │     └── FACES
 │
 └── AUDIO ANALYSIS
       ├── WAVEFORM
       ├── RMS
       ├── VAD
       ├── SILENCE
       └── BREATHING
```

---

## 111. Resource Management

Límites estrictos de workers de CPU, RAM máxima, descriptores de archivo abiertos y tamaño de caché.

---

## 112. Parallelism

Análisis concurrente de activos independientes.

---

## 113. Ordering

El manifiesto de salida es determinista e independiente del orden de finalización de los workers.

---

## 114. Worker Failure

El fallo de un proceso worker aísla el activo afectado como `FAILED` mientras el resto continúa.

---

## 115. Memory Safety

Prohibido cargar vídeos completos en memoria RAM.

---

## 116. Streaming

Procesamiento obligatorio por buffers o streaming cuando sea aplicable.

---

## 117. Disk Budget

Límite de almacenamiento para caché configurable (`maxCacheBytes?: number`).

---

## 118. Cache Eviction

Eliminación de artefactos descartables (miniaturas, proxies) respetando manifiestos maestros.

---

## 119. External Tool Abstraction

```typescript
interface MediaToolProvider {
  probe(path: string): Promise<MediaProbe>;
  extractAudio(path: string, options: AudioOptions): Promise<string>;
  extractFrame(path: string, timestamp: number): Promise<string>;
}
```

---

## 120. Tool Discovery

Comprobación previa de la existencia y operatividad de herramientas del sistema (FFmpeg, FFprobe).

---

## 121. Tool Version

Registro de nombres y versiones exactas de las herramientas externas en el manifiesto de reproducibilidad.

---

## 122. Offline Requirement

La ingestión se ejecuta en su totalidad sin conectividad a Internet.

---

## 123. Network Prohibition

Prohibida la transmisión de datos audiovisuales a servidores remotos durante la ingestión.

---

## 124. External AI

Modelos de análisis locales obligatorios; prohibidas APIs de pago como dependencias requeridas.

---

## 125. Analysis Provider Interface

```typescript
interface AnalysisProvider<TInput, TResult> {
  readonly id: string;
  readonly version: string;
  analyze(input: TInput): Promise<TResult>;
}
```

---

## 126. Replaceability

Implementaciones intercambiables (`LocalFaceDetector`, `LocalVAD`, `LocalSceneDetector`) sobre la misma interfaz.

---

## 127. Analyzer Registry

```typescript
interface AnalyzerRegistry {
  register(provider: AnalysisProvider<any, any>): void;
  resolve(id: string): AnalysisProvider<any, any>;
}
```

---

## 128. Analyzer Configuration

Configuración desacoplada por cada analizador.

---

## 129. Configuration Example

```json
{
  "ingestion": {
    "recursive": true,
    "hashAlgorithm": "sha256",
    "generateThumbnails": true,
    "generateProxies": false,
    "speechDetection": true,
    "faceDetection": true,
    "sceneDetection": true
  }
}
```

---

## 130. Analysis Output Contract

```typescript
interface AnalysisResult<T> {
  assetId: string;
  analyzerId: string;
  analyzerVersion: string;
  success: boolean;
  result?: T;
  warnings?: string[];
  errors?: string[];
}
```

---

## 131. Confidence Semantics

Confianzas normalizadas en el intervalo:
$$\text{confidence} \in [0.0, 1.0]$$

---

## 132. Score Semantics

Puntuaciones de calidad en escala:
$$\text{qualityScore} \in [0, 100]$$

---

## 133. Semantic Tags

```typescript
interface SemanticTag {
  value: string;
  confidence: number;
  source: string;
}
```

---

## 134. Tag Examples

`food`, `street`, `building`, `car`, `person`, `landscape`, `restaurant`, `museum`, `hotel`, `ocean`, `mountain`, `night`, `sunset`.

---

## 135. Tag Source

Orígenes identificados: `MODEL`, `FILENAME`, `FOLDER`, `USER`, `METADATA`.

---

## 136. Tag Conflict

Conservación ponderada de discrepancias entre fuentes sin sobrescritura ciega.

---

## 137. Priority

$$\text{USER} > \text{EXPLICIT METADATA} > \text{MODEL} > \text{FILENAME} > \text{FOLDER}$$

---

## 138. Asset Classification Handoff

La salida provee la metadata lista para que el `VlogFootageClassifier` decida la categoría final.

---

## 139. No Premature Classification

La ingestión genera candidatos e indicadores técnicos; no toma la decisión editorial final de montaje.

---

## 140. Data Flow to Classifier

```
Asset
 ├── video metadata
 ├── audio analysis
 ├── speech regions
 ├── face regions
 ├── motion
 ├── quality
 ├── semantic tags
 └── thumbnails
          │
          ▼
VlogFootageClassifier
```

---

## 141. Data Flow to Jump Cutter

$$\text{speech regions} + \text{silence regions} + \text{breath regions} + \text{transcript} \longrightarrow \text{VlogJumpCutEngine}$$

---

## 142. Data Flow to Punch-In

$$\text{face tracks} + \text{eye anchors} + \text{semantic emphasis} \longrightarrow \text{DynamicPunchIn}$$

---

## 143. Data Flow to Localization

Entrega de audio limpio normalizado, duración y regiones de habla para transcripción y traducción.

---

## 144. Data Flow to Pacing

Provisión de duración de fuente, cortes de escena y material disponible para adaptación de velocidad.

---

## 145. Manifest Example

```json
{
  "schemaVersion": "1.0.0",
  "ingestionVersion": "1.0.0",
  "assets": [
    {
      "id": "asset_8f31c2d9",
      "type": "VIDEO",
      "path": "raw/guadalajara_001.mov",
      "hash": {
        "algorithm": "sha256",
        "value": "..."
      },
      "duration": 42.18,
      "video": {
        "width": 3840,
        "height": 2160,
        "fps": 29.97,
        "frameRateMode": "VFR"
      },
      "audio": {
        "hasAudio": true,
        "sampleRate": 48000,
        "channels": 2
      }
    }
  ]
}
```

---

## 146. Required Tests

Pruebas obligatorias de descubrimiento recursivo, archivos ocultos/no soportados, hashes SHA-256, duplicados, VFR, rotación, múltiples pistas de audio, VAD, silencios, miniaturas, tomas, movimiento, calidad, rostros, proxies, caché, reanudación, cancelación, fallos aislados, orden determinista y modo offline.

---

## 147. Property-Based Tests

$$\text{hash}(\text{file}) \equiv \text{hash}(\text{file}), \quad \text{assetId}(\text{content}) \equiv \text{assetId}(\text{content})$$

---

## 148. Invariants

$$\text{duration} \ge 0, \quad \text{width} > 0, \quad \text{height} > 0, \quad \text{fps} > 0, \quad \text{sampleRate} > 0, \quad \text{channels} > 0$$

---

## 149. Time Invariants

$$\text{start} \ge 0, \quad \text{end} > \text{start}, \quad \text{end} \le \text{mediaDuration}$$

---

## 150. No Negative Timestamps

Rechazo estricto de tiempos negativos.

---

## 151. Floating Point Policy

Tiempos representados en segundos como números IEEE 754 de 64 bits con tolerancia epsilon centralizada.

---

## 152. Frame Conversion

Función centralizada para conversiones $\text{frameIndex} \longleftrightarrow \text{timestamp}$.

---

## 153. Timebase

Conversión a través del adaptador multimedia sin divisiones directas arbitrarias.

---

## 154. Exactness

Prohibido asumir $1\text{ frame} = 1/30\text{ s}$ en metraje que no sea estrictamente CFR 30.

---

## 155. Audio/Video Sync

Conservación de timestamps iniciales de cada stream multimedia.

---

## 156. Stream Start Time

Almacenamiento de `streamStartTime?: number`.

---

## 157. Sync Validation

Detección de desalineaciones significativas entre el inicio de audio y video.

---

## 158. Sync Warning

Desviaciones apreciables emiten `AUDIO_VIDEO_SYNC_OFFSET`.

---

## 159. Corrupt Media

Verificación de integridad mediante decodificación efectiva de muestras, no solo apertura de cabeceras.

---

## 160. Decode Validation

Muestreo de primer fotograma, fotograma intermedio, último fotograma válido y segmento de audio.

---

## 161. Decode Failure

Fallo de decodificación marca el activo como `CORRUPT_MEDIA`.

---

## 162. Last Frame

Uso de estrategias seguras para consultar el último fotograma sin desbordar la duración teórica.

---

## 163. Thumbnail Failure

El fallo al renderizar una miniatura emite advertencia pero no invalida un activo reproducible.

---

## 164. Analysis Degradation

Fallo en analizadores secundarios degrada el activo a `PARTIAL` sin descartarlo.

---

## 165. Analysis Completeness

```typescript
type AnalysisCompleteness =
  | "COMPLETE"
  | "PARTIAL"
  | "FAILED";
```

---

## 166. Asset Status

```typescript
type AssetStatus =
  | "VALID"
  | "PARTIAL"
  | "UNSUPPORTED"
  | "CORRUPT"
  | "MISSING";
```

---

## 167. Ingestion Session

```typescript
interface IngestionSession {
  id: string;
  startedAt: string;
  endedAt?: string;
  status: "RUNNING" | "SUCCESS" | "FAILED" | "CANCELLED";
}
```

---

## 168. Logging

Logs estructurados con timestamp, nivel, módulo, assetId, código y mensaje.

---

## 169. Log Levels

`DEBUG`, `INFO`, `WARN`, `ERROR`.

---

## 170. Secret Handling

Prohibida la inclusión de credenciales, claves o tokens en los registros.

---

## 171. Performance Metrics

Métricas de observabilidad: tiempo de sondeo, hashing, análisis, miniatura, uso de CPU y pico de memoria.

---

## 172. Benchmark Requirement

Pruebas de rendimiento con conjuntos de 10, 100 y 1000 activos.

---

## 173. Large File Handling

Procesamiento por bloques/stream para activos de gran volumen.

---

## 174. Hash Memory Constraint

Prohibido cargar archivos gigantes en memoria para calcular el hash criptográfico.

---

## 175. Concurrency Configuration

```typescript
interface ConcurrencyConfig {
  maxWorkers: number;
  maxVideoWorkers?: number;
  maxAudioWorkers?: number;
}
```

---

## 176. Default Concurrency

Determinación automática de workers según núcleos disponibles registrada en la sesión.

---

## 177. Deterministic Output Ordering

Ordenamiento lexicográfico por ruta relativa en todos los manifiestos generados.

---

## 178. Unicode Paths

Soporte integral de nombres de carpetas y archivos con caracteres Unicode (tildes, eñes, diacríticos).

---

## 179. Spaces

Manejo robusto de rutas con espacios en blanco.

---

## 180. Windows Compatibility

Normalización de barras invertidas, letras de unidad y límites de longitud de ruta.

---

## 181. macOS/Linux Compatibility

Compatibilidad con rutas POSIX, permisos de ejecución y distinción de mayúsculas/minúsculas.

---

## 182. Case Sensitivity

La identidad lógica del activo no depende de la sensibilidad a mayúsculas del filesystem.

---

## 183. Permission Errors

Aislamiento y reporte individual de errores de permisos.

---

## 184. Read-Only Input Test

Verificación de que el subsistema opera con éxito cuando el directorio de entrada tiene permisos estrictos de solo lectura.

---

## 185. Original Integrity Test

$$\text{SHA-256}(\text{original}_{\text{before}}) \equiv \text{SHA-256}(\text{original}_{\text{after}})$$

---

## 186. No Mutation Test

Comprobación estricta de que fechas de modificación, tamaño y atributos de los originales no varían.

---

## 187. Manifest Atomicity

Escritura atómica de manifiestos mediante archivos temporales y renombrado final.

---

## 188. Temporary Output

Almacenamiento de archivos temporales estrictamente fuera de la carpeta de originales.

---

## 189. Directory Layout

```
project/
├── raw/
│   └── [ORIGINALES INMUTABLES]
│
├── .engine/
│   ├── cache/
│   ├── analysis/
│   ├── thumbnails/
│   ├── proxies/
│   ├── manifests/
│   └── logs/
│
├── project.json
└── exports/
```

---

## 190. Raw Directory Rule

El directorio `raw/` es estrictamente inmutable.

---

## 191. Cache Rule

El directorio `.engine/` es reconstruible en su totalidad.

---

## 192. Export Rule

El directorio `exports/` contiene únicamente los entregables finales.

---

## 193. Cleanup

Limpieza permitida en `.engine/cache`; prohibido purgar `raw/`.

---

## 194. Ingestion Completion Criteria

La ingestión concluye exitosamente cuando:
- [✓] Descubrimiento finalizado
- [✓] Hashes generados
- [✓] Sondas técnicas completadas
- [✓] Análisis requeridos finalizados
- [✓] Manifiesto emitido
- [✓] Reporte generado
- [✓] Validación completada

---

## 195. Partial Completion

Fallos en analizadores opcionales culminan en `PARTIAL SUCCESS` con advertencias registradas.

---

## 196. Hard Failure

La imposibilidad de generar el manifiesto maestro culmina en `FAILED`.

---

## 197. Handoff Contract

```typescript
interface IngestionOutput {
  manifestPath: string;
  reportPath: string;
  assetRegistry: AssetRegistry;
  analysisDirectory: string;
}
```

---

## 198. Consumer Contract

Los subsistemas posteriores consumen directamente los análisis cacheados sin volver a inspeccionar los archivos originales.

---

## 199. Analyzer Version Mismatch

Cambios de versión en un analizador invalidan su caché respectiva.

---

## 200. Configuration Hash

Los parámetros de configuración forman parte de la clave de caché.

---

## 201. Cache Key

$$\text{SHA-256}(\text{assetHash} + \text{analyzerId} + \text{analyzerVersion} + \text{configurationHash})$$

---

## 202. Schema Compatibility

Cambios incompatibles en el esquema del análisis incrementan la versión del motor.

---

## 203. No Hidden State

Los analizadores son funciones puras sin dependencias de estado mutable oculto o reloj de sistema.

---

## 204. Final Architecture

```
                  RAW MEDIA
                      │
                      ▼
               ┌─────────────┐
               │  DISCOVERY  │
               └──────┬──────┘
                      ▼
               ┌─────────────┐
               │   HASHING   │
               └──────┬──────┘
                      ▼
               ┌─────────────┐
               │    PROBE    │
               └──────┬──────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
       ┌───────────┐     ┌───────────┐
       │   VIDEO   │     │   AUDIO   │
       │  ANALYSIS │     │  ANALYSIS │
       └─────┬─────┘     └─────┬─────┘
             │                 │
             └────────┬────────┘
                      ▼
              ┌──────────────┐
              │   FEATURES   │
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │    CACHE     │
              └──────┬───────┘
                     ▼
              ┌──────────────┐
              │   MANIFEST   │
              └──────┬───────┘
                     ▼
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    CLASSIFIER   TRANSCRIBER   JUMP CUTTER
```

---

## 205. Definition of Done

- [ ] Recursive discovery
- [ ] File identity
- [ ] SHA-256 hashing
- [ ] Duplicate detection
- [ ] Stable Asset IDs
- [ ] Media probing
- [ ] Container detection
- [ ] Codec detection
- [ ] Resolution detection
- [ ] FPS detection
- [ ] CFR/VFR detection
- [ ] Rotation handling
- [ ] Duration handling
- [ ] Audio stream detection
- [ ] Multiple audio streams
- [ ] Sample-rate detection
- [ ] Channel detection
- [ ] RMS analysis
- [ ] Peak analysis
- [ ] Clipping detection
- [ ] VAD
- [ ] Silence detection
- [ ] Breath detection
- [ ] Waveform
- [ ] Thumbnail generation
- [ ] Contact sheets
- [ ] Shot detection
- [ ] Motion analysis
- [ ] Sharpness
- [ ] Exposure
- [ ] Quality scoring
- [ ] Face detection
- [ ] Face tracking
- [ ] Eye anchors
- [ ] Metadata extraction
- [ ] GPS extraction
- [ ] Timezone support
- [ ] Semantic candidates
- [ ] Proxy generation
- [ ] Cache
- [ ] Cache invalidation
- [ ] Resume
- [ ] Cancellation
- [ ] Structured logging
- [ ] Error isolation
- [ ] Resource limits
- [ ] Offline operation
- [ ] Path security
- [ ] Unicode paths
- [ ] Windows compatibility
- [ ] macOS compatibility
- [ ] Linux compatibility
- [ ] Read-only input
- [ ] Original integrity
- [ ] Atomic manifests
- [ ] Deterministic ordering
- [ ] Property tests
- [ ] Integration tests
- [ ] Performance benchmarks

---

## 206. Estado

**Documento:** `14-VLOG-INGESTION-AND-MEDIA-ANALYSIS-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

---

## 207. Regla de Implementación

Este documento define exclusivamente ingestión y análisis inicial. No deberá implementar dentro de este módulo:
- B-roll matching
- jump cuts definitivos
- traducción
- TTS
- pacing multilingüe
- edición narrativa
- exportación JSX

Esas responsabilidades pertenecen a módulos posteriores. El resultado de este documento deberá ser suficientemente completo para que dichos módulos no tengan que volver a inspeccionar innecesariamente el material original.
