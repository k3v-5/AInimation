# Multilingual Voiceover Engine

**Documento:** `17-MULTILINGUAL-VOICEOVER-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  
**Dependencias:** Documentos de arquitectura existentes + Documento 16  
**Consumidores:** Vlog Adaptive Pacing Engine, Subtitle Engine, Audio Engine, After Effects JSX Exporter  

---

## 1. Objetivo

Definir completamente el sistema de generación de locuciones multilingües offline para que el motor pueda producir automáticamente versiones lingüísticas de un mismo contenido sin depender de APIs comerciales.

Idiomas objetivo iniciales:
- `es-MX`
- `es-ES`
- `en-US`
- `en-GB`
- `pt-BR`
- `fr-FR`
- `de-DE`

El sistema deberá permitir ampliar posteriormente el catálogo de idiomas sin modificar el núcleo del pipeline.

---

## 2. Requisito Principal

Una producción deberá poder tener:
$$1\text{ video fuente} + 1\text{ guion semántico} + N\text{ idiomas}$$
y producir:
- `audio_es-MX.wav`
- `audio_es-ES.wav`
- `audio_en-US.wav`
- `audio_en-GB.wav`
- `audio_pt-BR.wav`
- `audio_fr-FR.wav`
- `audio_de-DE.wav`
junto con sus metadatos temporales correspondientes.

---

## 3. Restricción Offline

El procesamiento normal deberá funcionar sin API keys, servicios cloud, cuentas externas ni conexión a Internet. El motor considerará Internet como una dependencia opcional, nunca obligatoria.

---

## 4. Arquitectura

```
SOURCE SCRIPT
      │
      ▼
LANGUAGE NORMALIZER
      │
      ▼
LOCALIZATION INPUT
      │
      ├── translated text
      ├── language
      ├── locale
      └── pronunciation metadata
      │
      ▼
VOICE PROFILE RESOLVER
      │
      ▼
LOCAL TTS PROVIDER
      │
      ▼
RAW AUDIO
      │
      ▼
AUDIO NORMALIZER
      │
      ▼
TIMING ANALYZER
      │
      ├── word timings
      ├── phoneme timings
      ├── pauses
      └── duration
      │
      ▼
VOICEOVER PACKAGE
      │
      ├── WAV
      ├── transcript
      ├── timings
      └── metadata
```

---

## 5. Provider Abstraction

```typescript
interface TTSProvider {
  readonly id: string;
  readonly version: string;

  synthesize(request: TTSRequest): Promise<TTSResult>;
  listVoices(): Promise<VoiceDefinition[]>;
  supports(language: LanguageCode): boolean;
}
```

---

## 6. Provider Inicial

La primera implementación podrá utilizar motores locales como `Piper` u otros proveedores locales compatibles, siempre encapsulados detrás de `TTSProvider`.

---

## 7. Provider Registry

```typescript
interface TTSProviderRegistry {
  register(provider: TTSProvider): void;
  resolve(language: LanguageCode, preferredProvider?: string): TTSProvider;
  listAvailable(): TTSProvider[];
}
```

---

## 8. Provider Priority

Resolución obligatoria:
1. Provider solicitado explícitamente
2. Provider local compatible
3. Provider local alternativo
4. Fallo controlado (prohibido acudir a la nube si offline está activo).

---

## 9. Offline Mode

```typescript
interface VoiceoverRuntimeConfig {
  offlineOnly: boolean;
}
```
Con `offlineOnly = true` queda terminantemente prohibido utilizar proveedores remotos.

---

## 10. Language Code

```typescript
type LanguageCode =
  | "es-MX"
  | "es-ES"
  | "en-US"
  | "en-GB"
  | "pt-BR"
  | "fr-FR"
  | "de-DE";
```

---

## 11. Language Extensibility

El núcleo admitirá `type CustomLanguageCode = string;` mediante registro modular de capacidades.

---

## 12. Voice Definition

```typescript
interface VoiceDefinition {
  id: string;
  providerId: string;
  language: LanguageCode;
  gender?: "female" | "male" | "neutral";
  locale: string;
  sampleRate: number;
  supportsWordTimings: boolean;
  supportsPhonemeTimings: boolean;
}
```

---

## 13. Voice Profile

```typescript
interface VoiceProfile {
  id: string;
  language: LanguageCode;
  provider: string;
  voiceId: string;
  speakingRate: number;
  pitch: number;
  volume: number;
}
```

---

## 14. Voice Identity

Identificación unívoca mediante:
$$\text{providerId} + \text{voiceId} + \text{voiceVersion}$$

---

## 15. Voice Lock

Bloqueo explícito (`voiceLock: true`) para impedir que actualizaciones del catálogo varíen la voz de una producción consolidada.

---

## 16. Voice Fallback

$$\text{Voz principal} \longrightarrow \text{Voz mismo locale} \longrightarrow \text{Voz mismo idioma} \longrightarrow \text{Fallo registrado}$$

---

## 17. No Silent Voice Replacement

Prohibido sustituir una voz silenciosamente sin registrar `requestedVoice`, `resolvedVoice` y `reason`.

---

## 18. TTS Request

```typescript
interface TTSRequest {
  text: string;
  language: LanguageCode;
  voice: VoiceProfile;
  outputFormat: AudioFormat;
  speakingRate: number;
  pitch: number;
  volume: number;
  metadata?: Record<string, string>;
}
```

---

## 19. Output Audio

Formato maestro obligatorio:
$$\text{WAV, PCM 16-bit, 44.1 kHz, Mono}$$

---

## 20. Internal Audio Format

Toda salida de provider se convierte al formato interno antes de entregarse a otros subsistemas.

---

## 21. Audio Normalization

$$\text{Decodificación} \longrightarrow \text{Conversión mono} \longrightarrow \text{Resampling a 44.1 kHz} \longrightarrow \text{Inspección pico} \longrightarrow \text{Normalización EBU R128} \longrightarrow \text{Verificación DC} \longrightarrow \text{PCM 16-bit}$$

---

## 22. Clipping Protection

$$\text{sample} \in [-1.0, +1.0] \quad (\text{cero distorsión digital})$$

---

## 23. Peak Ceiling

Techo técnico máximo: $-1.0\text{ dBFS}$.

---

## 24. Loudness Target

```typescript
interface LoudnessConfig {
  targetLUFS: number;
  maxTruePeakDbTP: number;
}
```

---

## 25. Silence Trimming

Detección y registro de silencios limítrofes (`leadingSilence`, `trailingSilence`).

---

## 26. Silence Policy

El sistema no eliminará pausas internas del discurso; solo los silencios iniciales y finales son recortados.

---

## 27. Internal Pause Preservation

Pausas expresivas internas (*"Y entonces... ocurrió"*) se preservan intactas.

---

## 28. SSML / Prosody Abstraction

```typescript
interface SpeechMarkup {
  text: string;
  breaks?: SpeechBreak[];
  emphasis?: SpeechEmphasis[];
  pronunciation?: PronunciationOverride[];
}
```

---

## 29. Speech Break

```typescript
interface SpeechBreak {
  position: number;
  duration: number;
}
```

---

## 30. Emphasis

```typescript
interface SpeechEmphasis {
  start: number;
  end: number;
  level: "reduced" | "normal" | "strong";
}
```

---

## 31. Pronunciation Override

```typescript
interface PronunciationOverride {
  text: string;
  phonetic?: string;
  ipa?: string;
  providerSpecific?: Record<string, string>;
}
```

---

## 32. Proper Names

Reglas fonéticas para topónimos y términos técnicos (`Guadalajara`, `México`, `Aguascalientes`, `YouTube`, `After Effects`).

---

## 33. Brand Pronunciation

```typescript
interface PronunciationDictionaryEntry {
  token: string;
  language: LanguageCode;
  pronunciation: string;
}
```

---

## 34. Number Normalization

Conversión de cifras a palabras habladas (*"50 pesos"* $\to$ *"cincuenta pesos"*) sin alterar el texto visible del subtítulo.

---

## 35. Date Normalization

Formateo fonético de fechas según las convenciones orales de cada locale.

---

## 36. Time Normalization

Formateo fonético de horas (`8:42 PM`) adaptado a cada idioma.

---

## 37. Currency Normalization

Pronunciación adecuada de divisas (`MXN`, `USD`, `EUR`, `BRL`, `GBP`).

---

## 38. Abbreviation Normalization

Expansión oral de abreviaturas (`km`, `kg`, `cm`, `%`, `GPS`, `AI`, `API`).

---

## 39. Localization Separation

El motor de voz no traduce; recibe texto localizado y sintetiza audio localizado.

---

## 40. Source Text Identity

Toda locución conserva referencias a `sourceScriptId`, `localizedScriptId` e `idioma`.

---

## 41. Segment-Based Synthesis

```typescript
interface VoiceoverSegment {
  id: string;
  text: string;
  startReference?: number;
  endReference?: number;
}
```

---

## 42. Segment Synthesis

Textos extensos se procesan por segmentos atómicos independientes y se ensamblan posteriormente.

---

## 43. Segment Join

Unión limpia sin clicks, discontinuidades de fase ni gaps no deseados.

---

## 44. Inter-Segment Silence

Los silencios entre oraciones forman parte explícita de la línea temporal maestra.

---

## 45. Voiceover Timeline

```typescript
interface VoiceoverTimeline {
  segments: VoiceoverTimelineSegment[];
  totalDuration: number;
}
```

---

## 46. Timeline Segment

```typescript
interface VoiceoverTimelineSegment {
  id: string;
  sourceTextSegmentId: string;
  audioStart: number;
  audioEnd: number;
  speechStart: number;
  speechEnd: number;
}
```

---

## 47. Word Timing

```typescript
interface VoiceWordTiming {
  word: string;
  normalizedWord: string;
  start: number;
  end: number;
  confidence?: number;
}
```

---

## 48. Phoneme Timing

```typescript
interface VoicePhonemeTiming {
  phoneme: string;
  start: number;
  end: number;
}
```

---

## 49. Timing Source

Fuentes declaradas: `PROVIDER_NATIVE`, `ALIGNER_LOCAL`, `ESTIMATED`.

---

## 50. Timing Confidence

```typescript
interface TimingMetadata {
  source: string;
  confidence: number;
}
```

---

## 51. Missing Timings

Si el proveedor nativo no emite timestamps, se aplica alineación forzada local (*forced alignment*).

---

## 52. Alignment Failure

Si la alineación falla, se preserva el audio y se marca la degradación temporal.

---

## 53. Degraded Mode

Registro de `TIMING_DEGRADED` proveyendo únicamente la duración global al motor de pacing.

---

## 54. Determinism

Misma entrada de texto, voz, configuración y versión de modelo genera resultados reproducibles.

---

## 55. Audio Hash

Cálculo de hash `SHA-256` sobre el archivo WAV emitido.

---

## 56. Cache Key

$$\text{SHA-256}(\text{textHash} + \text{language} + \text{voiceId} + \text{providerId} + \text{version} + \text{rate} + \text{pitch} + \text{normConfig})$$

---

## 57. Cache Hit

Acierto en caché reutiliza el audio existente sin invocar al motor TTS.

---

## 58. Cache Invalidation

Variaciones en el texto, voz o parámetros de audio invalidan la entrada en caché.

---

## 59. Cache Corruption

Archivos de caché corruptos o truncados se purgan y regeneran de inmediato.

---

## 60. Atomic Writes

$$\text{Archivo temporal} \longrightarrow \text{Validación técnica} \longrightarrow \text{Renombrado atómico}$$

---

## 61. Parallelization

Síntesis concurrente de pistas para diferentes idiomas (`es-MX`, `en-US`, `pt-BR`, etc.).

---

## 62. Concurrency Limit

Límite de trabajadores concurrentes (`maxConcurrentTTSJobs: number`) para evitar sobrecarga de CPU/RAM.

---

## 63. Queue

Procesamiento mediante cola determinista de tareas.

---

## 64. Job Identity

```typescript
interface VoiceoverJob {
  id: string;
  language: LanguageCode;
  scriptId: string;
  voiceId: string;
  status:
    | "QUEUED"
    | "RUNNING"
    | "COMPLETED"
    | "FAILED"
    | "CANCELLED";
}
```

---

## 65. Retry Policy

Hasta $2\text{ reintentos}$ ante fallos transitorios locales del proceso.

---

## 66. Retry Safety

Los reintentos limpian archivos temporales para no duplicar datos ni corromper el estado.

---

## 67. Cancellation

Cancelación limpia de tareas sin dejar residuos huérfanos en disco.

---

## 68. Progress

Estados reportados: `queued`, `loading model`, `synthesizing`, `normalizing`, `aligning`, `writing`, `validating`, `completed`.

---

## 69. Model Loading

Los pesos de modelos locales se retienen en memoria entre frases consecutivas del mismo idioma.

---

## 70. Model Memory

Descarga automática de modelos ante presión crítica de memoria RAM.

---

## 71. Model Registry

```typescript
interface TTSModelDefinition {
  id: string;
  version: string;
  languages: LanguageCode[];
  localPath: string;
  sizeBytes: number;
}
```

---

## 72. Model Verification

Comprobación previa de existencia, permisos, versión e integridad criptográfica.

---

## 73. Missing Model

Emisión de error estructurado `MODEL_UNAVAILABLE` con instrucciones de resolución.

---

## 74. No Automatic Download

Con `offlineOnly = true` queda prohibida la descarga desatendida de modelos desde la red.

---

## 75. Optional Model Installation

La provisión de modelos es una operación administrativa desacoplada del runtime de renderizado.

---

## 76. Locale Behavior

Tratamiento independiente y específico para `es-MX` frente a `es-ES`.

---

## 77. Locale Fallback

$$\text{es-MX} \longrightarrow \text{es genérico} \longrightarrow \text{Fallback registrado}$$

---

## 78. Accent Preservation

Prohibido sustituir `es-MX` por `es-ES` silenciosamente si se solicitó expresamente la variante mexicana.

---

## 79. Voice Consistency

Todos los segmentos de un idioma dentro de la producción emplean la misma voz salvo instrucción explícita.

---

## 80. Segment Voice Override

```typescript
interface SegmentVoiceOverride {
  segmentId: string;
  voiceId: string;
}
```

---

## 81. Voice Mixing Warning

La alternancia no justificada de voces emite `WARNING: VOICE_CONTINUITY_BREAK`.

---

## 82. Speaking Rate

Multiplicador relativo con valor neutral $1.00\text{x}$.

---

## 83. Allowed Rate Range

Rango admisible para generación base: $[0.80\text{x}, 1.20\text{x}]$.

---

## 84. Adaptive Rate

Ajustes finos solicitados por el motor de pacing en el margen $[0.95\text{x}, 1.05\text{x}]$.

---

## 85. Rate Quality Protection

Peticiones fuera de $[0.80\text{x}, 1.20\text{x}]$ emiten error `RATE_OUT_OF_RANGE`.

---

## 86. Pitch

Control independiente de pitch acústico (`pitch: number`).

---

## 87. Pitch Safety

Prohibido alterar el pitch de manera automática para compensar desajustes de tiempo.

---

## 88. Volume

El volumen nativo del TTS se somete al pipeline general de normalización sonora.

---

## 89. Background Music Compatibility

Suministro de envolventes de actividad vocal para el ducking automático de la música.

---

## 90. Voice Activity Metadata

El paquete incluye marcadores exactos de `speechStart`, `speechEnd` y regiones de silencio.

---

## 91. Breath Metadata

Inclusión de eventos respiratorios audibles para la coordinación editorial.

---

## 92. Output Package

```typescript
interface VoiceoverPackage {
  language: LanguageCode;
  audioPath: string;
  duration: number;
  words: VoiceWordTiming[];
  phonemes?: VoicePhonemeTiming[];
  pauses: VoicePause[];
  metadata: VoiceoverMetadata;
}
```

---

## 93. Metadata

```typescript
interface VoiceoverMetadata {
  providerId: string;
  providerVersion: string;
  voiceId: string;
  voiceVersion: string;
  modelId: string;
  modelVersion: string;
  sampleRate: number;
  channels: number;
  bitDepth: number;
  sha256: string;
  generatedAt: string;
}
```

---

## 94. Reproducibility Metadata

Registro de `scriptHash`, `configurationHash`, `cacheKey` y `engineVersion`.

---

## 95. Audio Validation

Validación previa de cabeceras WAV, 44.1 kHz, 16-bit mono, duración positiva y ausencia de NaNs o clipping.

---

## 96. Silence Validation

Detección de audios mudos por fallo del modelo emitiendo `TTS_EMPTY_AUDIO`.

---

## 97. Excessive Silence

Proporciones anómalas de silencio emiten `WARNING: EXCESSIVE_SILENCE`.

---

## 98. Text Empty

Segmentos sin contenido textual resuelven a `EMPTY_SCRIPT_SEGMENT` sin invocar síntesis.

---

## 99. Unicode

Preservación de caracteres latinos extendidos (`á`, `é`, `í`, `ó`, `ú`, `ñ`, `ü`, `ç`, `ß`) y diacríticos.

---

## 100. Emoji Speech Policy

```typescript
emojiSpeechMode:
  | "IGNORE"
  | "DESCRIBE"
  | "PROVIDER_DEFAULT";
```
Por defecto: `IGNORE`.

---

## 101. Markdown Removal

Filtrado de caracteres puramente visuales (`**`, `##`, `[]`) antes de la síntesis vocal.

---

## 102. Caption Text vs Speech Text

Separación estricta entre texto visual en pantalla (`displayText`) y texto enviado a la voz (`speechText`).

---

## 103. Travel Overlay Compatibility

Permite incluir emojis e iconos en badges visuales sin que la voz intente vocalizarlos.

---

## 104. Pronunciation Dictionary Priority

$$\text{Segment override} > \text{Project dict} > \text{Language dict} > \text{Provider rule} > \text{Default}$$

---

## 105. Project Dictionary

Diccionario local de proyecto `pronunciation.json`.

---

## 106. Language Dictionary

Diccionarios específicos por idioma (`pronunciation/es-MX.json`, etc.).

---

## 107. Provider-Specific Rules

Reglas exclusivas de un motor quedan aisladas dentro de su adaptador correspondiente.

---

## 108. Error Taxonomy

- `TTS_PROVIDER_NOT_FOUND`
- `TTS_LANGUAGE_UNSUPPORTED`
- `TTS_VOICE_NOT_FOUND`
- `TTS_MODEL_UNAVAILABLE`
- `TTS_SYNTHESIS_FAILED`
- `TTS_EMPTY_AUDIO`
- `TTS_AUDIO_INVALID`
- `TTS_ALIGNMENT_FAILED`
- `TTS_RATE_OUT_OF_RANGE`
- `TTS_CACHE_CORRUPTED`
- `TTS_CANCELLED`
- `TTS_RESOURCE_EXHAUSTED`

---

## 109. Error Object

```typescript
interface VoiceoverError {
  code: string;
  message: string;
  language: LanguageCode;
  segmentId?: string;
  providerId?: string;
  recoverable: boolean;
}
```

---

## 110. Failure Isolation

El fallo en un idioma (ej. `fr-FR`) no invalida las pistas exitosas (`es-MX`, `en-US`, `pt-BR`).

---

## 111. Multi-Language Job Result

```typescript
interface MultilingualVoiceoverResult {
  completed: VoiceoverPackage[];
  failed: VoiceoverFailure[];
}
```

---

## 112. Partial Success

El proyecto puede proseguir si los idiomas fallidos están marcados como opcionales.

---

## 113. Required Languages

```typescript
requiredLanguages: LanguageCode[];
```
El fallo en un idioma requerido detiene el pipeline principal.

---

## 114. Optional Languages

Idiomas opcionales pueden fallar sin bloquear la producción maestra.

---

## 115. Language Ordering

El orden de procesamiento no afecta la naturaleza determinista de las pistas generadas.

---

## 116. Deterministic Language Set

Lista de idiomas ordenada y normalizada antes de iniciar la orquestación de tareas.

---

## 117. Duplicate Language

Peticiones duplicadas para el mismo idioma se consolidan automáticamente.

---

## 118. Script Version Lock

Invalidez de audio si el hash del guion localizado no coincide con el registrado en caché.

---

## 119. Translation Version Lock

Registro vinculante de `translationVersion` y `translationHash`.

---

## 120. Audio/Script Integrity

Prohibido emparejar audios con guiones alterados sin advertencia explícita.

---

## 121. Subtitle Integration

Entrega directa de timestamps palabra por palabra al `Subtitle Engine` para evitar re-alineaciones innecesarias.

---

## 122. Viral Moment Integration

El detector de momentos virales opera sobre el audio del idioma destino analizando RMS y cadencia vocal.

---

## 123. Pacing Integration

El motor de pacing recibe duraciones, límites de oraciones y pausas por cada idioma.

---

## 124. Visual Sync Principle

La locución nunca modifica directamente transformaciones de cámara, B-Roll ni estilos de subtítulos.

---

## 125. Master Output

Estructura de entrega por idioma con archivos `audio.wav`, `timing.json` y `metadata.json`.

---

## 126. Manifest

```typescript
interface VoiceoverManifest {
  projectId: string;
  scriptHash: string;
  languages: VoiceoverLanguageManifest[];
}
```

---

## 127. Language Manifest

```typescript
interface VoiceoverLanguageManifest {
  language: LanguageCode;
  status: "READY" | "FAILED";
  audioPath?: string;
  timingPath?: string;
  metadataPath?: string;
  duration?: number;
  sha256?: string;
}
```

---

## 128. Test: Provider Resolution

Comprobación de que cada idioma activa el proveedor local adecuado.

---

## 129. Test: Offline Enforcement

Rechazo estricto de cualquier petición que intente acceder a endpoints externos con `offlineOnly = true`.

---

## 130. Test: Voice Lock

Verificación de que una voz bloqueada no se sustituye ante cambios del catálogo.

---

## 131. Test: Cache

Comprobación de acierto en caché sin regeneración de audio ante entradas idénticas.

---

## 132. Test: Cache Invalidation

Comprobación de fallo de caché y regeneración al variar la voz o parámetros de velocidad.

---

## 133. Test: Language Isolation

Verificación de que el fallo forzado en `fr-FR` no altera la pista generada para `es-MX`.

---

## 134. Test: Unicode

Procesamiento correcto de caracteres con tildes y signos de apertura (*"¡Qué increíble! México está aquí"*).

---

## 135. Test: Display/Speech Separation

Verificación de que `displayText = "📍 Guadalajara"` se sintetiza como `speechText = "Guadalajara"`.

---

## 136. Test: Numbers

Conversión oral de *"50 pesos"* sin modificar el texto de presentación.

---

## 137. Test: Dates

Comprobación de que una fecha ISO emite locuciones fonéticas específicas por cada locale.

---

## 138. Test: Currency

Verificación de pronunciación adecuada para `MXN`, `USD`, `EUR`, `BRL` y `GBP`.

---

## 139. Test: Empty Text

Verificación de que un texto vacío no invoca llamadas al motor TTS.

---

## 140. Test: Invalid Audio

Comprobación de detección y rechazo de archivos WAV truncados o con cabecera corrupta.

---

## 141. Test: Clipping

Verificación de limitación estricta a $\le 0.0\text{ dBFS}$ en audios sintetizados.

---

## 142. Test: Timing

$$0 \le \text{word.start} < \text{word.end} \le \text{audio.duration}$$

---

## 143. Test: Timing Ordering

Progresión temporal monótona en las palabras alineadas.

---

## 144. Test: Phoneme Ordering

Progresión temporal monótona en los fonemas alineados.

---

## 145. Property-Based Test

Textos aleatorios de longitud variable generan siempre duraciones no negativas y timestamps en rango.

---

## 146. Property: Cache Determinism

Misma entrada genera idéntico cache key criptográfico.

---

## 147. Property: Language Isolation

Modificar el idioma altera obligatoriamente la clave de caché.

---

## 148. Property: Voice Isolation

Modificar la voz altera obligatoriamente la clave de caché.

---

## 149. Property: Rate Isolation

Modificar la velocidad altera obligatoriamente la clave de caché.

---

## 150. Property: Configuration Isolation

Modificar parámetros de normalización acústica invalida la caché.

---

## 151. Performance Test

Medición continua de tiempo de procesamiento, duración de audio, uso de CPU y factor de tiempo real (RTF).

---

## 152. Real-Time Factor

$$\text{RTF} = \frac{\text{processingTime}}{\text{audioDuration}}$$

---

## 153. Performance Target

$$\text{RTF} \le 1.0 \quad (\text{procesamiento más rápido o igual al tiempo real})$$

---

## 154. Resource Failure

Emisión de `TTS_RESOURCE_EXHAUSTED` y liberación de buffers ante presión de RAM.

---

## 155. Model Reuse Test

Comprobación de retención y reutilización de modelos en memoria para tareas sucesivas del mismo idioma.

---

## 156. Concurrency Test

Respeto estricto del límite máximo de trabajadores concurrentes (`maxConcurrentTTSJobs`).

---

## 157. Cancellation Test

Verificación de que un trabajo cancelado termina en estado `CANCELLED` sin artefactos parciales.

---

## 158. Atomic Output Test

Comprobación de que procesos interrumpidos no dejan archivos WAV truncados marcados como válidos.

---

## 159. Manifest Consistency Test

Comprobación de que todo idioma marcado como `READY` posee audio, timings y hash verificados.

---

## 160. Golden Audio Tests

Comparación de duraciones, RMS, picos, LUFS y distribución de silencios contra archivos dorados de referencia.

---

## 161. Provider Contract Tests

Suite común de pruebas para validar cualquier proveedor: soporte de idioma, síntesis, validación y manejo de errores.

---

## 162. Mock Provider

Inclusión de `DeterministicMockTTSProvider` para tests unitarios rápidos sin carga de modelos pesados.

---

## 163. Mock Provider

El proveedor mock emite audio precalculado y timestamps deterministas estables.

---

## 164. Integration Tests

Prueba de integración integral:
$$\text{Guion localizado} \longrightarrow \text{TTS} \longrightarrow \text{Audio} \longrightarrow \text{Timings} \longrightarrow \text{Adaptive Pacing Engine}$$

---

## 165. Regression Test

Conservación de fixtures multilingües estables en los 7 idiomas oficiales.

---

## 166. No Network Test

Ejecución verificada con adaptador de red desactivado demostrando operatividad 100% offline.

---

## 167. Network Dependency Detection

Cualquier intento de conexión a Internet durante las pruebas offline marca fallo inmediato (`FAIL`).

---

## 168. Security

Prohibido transmitir textos de guiones o audios a servidores externos.

---

## 169. Filesystem Isolation

Escritura restringida al espacio de trabajo autorizado del proyecto.

---

## 170. Path Safety

Bloqueo estricto de secuencias de escape de directorio (`../`) en identificadores de idioma o voz.

---

## 171. Filename Normalization

Nombres normalizados y seguros (`audio_es-MX.wav`, `audio_en-US.wav`).

---

## 172. Manifest Schema Version

$$\text{schemaVersion} = \text{"1.0.0"}$$

---

## 173. Backward Compatibility

Estrategia formal de migración ante variaciones de esquema.

---

## 174. Observability

Registro estructurado de eventos: `JOB_CREATED`, `MODEL_LOADED`, `CACHE_HIT`, `SYNTHESIS_COMPLETED`, `ALIGNMENT_COMPLETED`, `JOB_COMPLETED`.

---

## 175. Debug Mode

Retención de audios intermedios y transcripciones fonéticas cuando `debug = true`.

---

## 176. Privacy

Eliminación de archivos temporales según las directivas de privacidad del proyecto.

---

## 177. Cleanup

Limpieza de temporales tras la validación y emisión del manifiesto definitivo.

---

## 178. Rebuild

Capacidad de regenerar de forma determinista cualquier pista a partir de sus entradas y configuración.

---

## 179. No Hidden State

Ausencia de dependencias de reloj de sistema o semillas aleatorias ocultas para determinar el audio.

---

## 180. Definition of Done

- [ ] TTSProvider abstraction
- [ ] Provider registry
- [ ] Offline enforcement
- [ ] Language registry
- [ ] Locale handling
- [ ] Voice registry
- [ ] Voice profile
- [ ] Voice lock
- [ ] Voice fallback
- [ ] Model registry
- [ ] Model validation
- [ ] Local model loading
- [ ] Segment synthesis
- [ ] Speech markup abstraction
- [ ] Pronunciation dictionary
- [ ] Number normalization
- [ ] Date normalization
- [ ] Currency normalization
- [ ] Abbreviation normalization
- [ ] Display/speech separation
- [ ] WAV normalization
- [ ] Loudness normalization
- [ ] Clipping protection
- [ ] Silence analysis
- [ ] Word timings
- [ ] Phoneme timings
- [ ] Local alignment fallback
- [ ] Timing confidence
- [ ] Cache
- [ ] Cache invalidation
- [ ] Atomic writes
- [ ] Parallel language processing
- [ ] Concurrency limits
- [ ] Job queue
- [ ] Retry policy
- [ ] Cancellation
- [ ] Progress reporting
- [ ] Resource management
- [ ] Error taxonomy
- [ ] Partial success
- [ ] Required languages
- [ ] Manifest
- [ ] Hashing
- [ ] Reproducibility metadata
- [ ] Security validation
- [ ] Mock provider
- [ ] Provider contract tests
- [ ] Property-based tests
- [ ] Golden tests
- [ ] Regression tests
- [ ] Offline tests
- [ ] Performance tests

---

## 181. Estado del Documento

**Documento:** `17-MULTILINGUAL-VOICEOVER-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

---

## 182. Regla de Implementación

Este documento define exclusivamente:
$$\text{TTS local} + \text{Voces} + \text{Modelos} + \text{Normalización fonética} + \text{Generación WAV} + \text{Timings} + \text{Caché} + \text{Validación}$$

No define traducción, selección de B-Roll, pacing visual, subtítulos, música, SFX, overlays ni render JSX. Esos subsistemas consumirán este plan mediante contratos explícitos.

---

## 183. Contrato de Salida Obligatorio

```typescript
interface VoiceoverPackage {
  language: LanguageCode;
  audioPath: string;
  duration: number;
  words: VoiceWordTiming[];
  phonemes?: VoicePhonemeTiming[];
  pauses: VoicePause[];
  metadata: VoiceoverMetadata;
}
```
Cualquier proveedor o adaptador deberá entregar sus resultados ajustados estrictamente a este contrato.
