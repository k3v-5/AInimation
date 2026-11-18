# Multilingual Voiceover Engine

**Documento:** `07-MULTILINGUAL-VOICEOVER-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog Multilingual Expansion  
**Dependencias:** `LocalWhisperTranscriptionBridge`, Audio Engine, Timeline Engine, `VlogAdaptivePacingEngine`, Media Cache, Export Pipeline  

---

## 1. Objetivo

Definir el sistema responsable de generar locuciones sintéticas locales para múltiples idiomas y variantes regionales, sin depender de APIs de pago ni servicios cloud.

Idiomas iniciales:
- `es-MX`
- `es-ES`
- `en-US`
- `en-GB`
- `pt-BR`
- `fr-FR`
- `de-DE`

El sistema deberá producir audio reproducible, normalizado, cacheable y temporalmente alineable con el guion.

---

## 2. Principio fundamental

La arquitectura deberá separar:

$$\text{Texto} \longrightarrow \text{Normalización lingüística} \longrightarrow \text{Selección de voz} \longrightarrow \text{TTS local} \longrightarrow \text{Audio bruto} \longrightarrow \text{Normalización} \longrightarrow \text{Alineación temporal} \longrightarrow \text{Voiceover Track}$$

El TTS no será responsable de decidir el montaje.

---

## 3. Componentes

`MultilingualVoiceoverEngine` se compone de:
- `LanguageResolver`
- `TextNormalizer`
- `VoiceRegistry`
- `VoiceSelector`
- `LocalTTSProvider`
- `TTSAudioGenerator`
- `AudioNormalizer`
- `SpeechAligner`
- `VoiceoverSegmenter`
- `VoiceoverCache`
- `VoiceoverValidator`
- `VoiceoverArtifactWriter`

---

## 4. Input

```typescript
interface VoiceoverRequest {
  projectId: string;
  language: SupportedLanguage;
  text: string;
  voiceId?: string;
  configuration: VoiceoverConfig;
}
```

---

## 5. Supported Language

```typescript
type SupportedLanguage =
  | "es-MX"
  | "es-ES"
  | "en-US"
  | "en-GB"
  | "pt-BR"
  | "fr-FR"
  | "de-DE";
```

---

## 6. Language Is Not Voice

El idioma y la voz deberán ser entidades independientes.

Ejemplo:
- $\text{language} = \text{es-MX}$
- $\text{voiceId} = \text{voice\_es\_mx\_female\_01}$

No se deberá inferir una voz arbitraria cuando el proyecto solicita una voz concreta.

---

## 7. Voice Registry

```typescript
interface VoiceDefinition {
  id: string;
  language: SupportedLanguage;
  provider: string;
  model: string;
  gender?: "female" | "male" | "neutral";
  style?: string;
  sampleRate: number;
  version: string;
}
```

---

## 8. Voice Registry File

Las voces disponibles deberán declararse en un archivo versionado:
`voices.json`

Ejemplo:
```json
{
  "id": "voice_es_mx_01",
  "language": "es-MX",
  "provider": "local",
  "model": "MODEL_NAME",
  "version": "1.0.0"
}
```

---

## 9. No Hardcoded Voice

El código no deberá contener:
$$\text{if } \text{language} == \text{"es-MX"} \implies \text{use voice X}$$
Las asociaciones deberán resolverse mediante `VoiceRegistry`.

---

## 10. Local TTS Provider

```typescript
interface LocalTTSProvider {
  synthesize(
    text: string,
    voice: VoiceDefinition,
    options: TTSOptions
  ): Promise<TTSAudioResult>;
}
```

---

## 11. TTS Options

```typescript
interface TTSOptions {
  speakingRate: number;
  pitch?: number;
  volume?: number;
  outputFormat: "wav";
  sampleRate: number;
}
```

---

## 12. Offline Contract

Un provider marcado como `LOCAL` deberá funcionar sin:
- API key;
- conexión a Internet;
- servicio remoto;
- cuota;
- coste por carácter;
- coste por minuto.

---

## 13. Provider Abstraction

El engine no deberá depender directamente de Piper, Edge-TTS u otro motor concreto. La arquitectura deberá permitir `PiperProvider`, `OtherLocalProvider`, `FutureLocalProvider` mediante la misma interfaz.

---

## 14. Provider Selection

La selección seguirá:
$$\text{requested voice} > \text{language-compatible voice} > \text{configured fallback} > \text{error}$$

---

## 15. No Silent Fallback

Si se solicita `voice_es_mx_02` y no existe:
$$\text{VoiceNotFoundError}$$
No deberá sustituirse silenciosamente por otra voz.

---

## 16. Explicit Fallback

La configuración podrá definir:

```typescript
interface VoiceFallbackPolicy {
  enabled: boolean;
  fallbackVoiceId?: string;
  allowCrossRegionFallback: boolean;
}
```

---

## 17. Regional Fallback

Por defecto, $\text{es-MX} \to \text{es-ES}$ deberá estar `disabled`. La región forma parte del resultado editorial.

---

## 18. Text Normalization

Antes de TTS se deberá normalizar:
- espacios;
- saltos de línea;
- caracteres invisibles;
- Unicode equivalente;
- números;
- símbolos;
- abreviaturas;
- URLs;
- emojis cuando corresponda.

---

## 19. Unicode Normalization

Se utilizará una forma Unicode determinista, por ejemplo:
$$\text{NFC}$$

---

## 20. Number Normalization

El TTS no deberá recibir necesariamente `"2026"` si el objetivo lingüístico requiere `"dos mil veintiséis"`. La conversión deberá depender del idioma.

---

## 21. Currency

Ejemplo: `"$1,250"` deberá convertirse mediante reglas lingüísticas antes de TTS cuando sea necesario.

---

## 22. Dates

Las fechas deberán normalizarse según idioma (ej. `2026-09-01` a una representación hablada localizada).

---

## 23. Time

Ejemplo: `8:42 PM` deberá transformarse según el idioma y configuración editorial.

---

## 24. Acronyms

Los acrónimos deberán disponer de reglas explícitas (ej. `GPS`, `AI`, `CEO` no deberán pronunciarse siempre letra por letra).

---

## 25. URLs

Las URLs deberán poder convertirse a una forma pronunciable o excluirse de TTS según configuración.

---

## 26. Emoji

Los emojis deberán disponer de política:

```typescript
type EmojiSpeechPolicy =
  | "IGNORE"
  | "SPEAK"
  | "REPLACE_WITH_LABEL";
```
Valor inicial: `IGNORE`.

---

## 27. Punctuation

La puntuación deberá conservarse cuando afecte la prosodia (`,`, `.`, `?`, `!`, `:`, `;`).

---

## 28. Sentence Segmentation

El texto deberá dividirse en unidades lingüísticas:

```typescript
interface TextSegment {
  id: string;
  text: string;
  startChar: number;
  endChar: number;
}
```

---

## 29. TTS Chunking

No se deberá asumir que un motor TTS puede sintetizar arbitrariamente un documento completo. El engine deberá dividir textos extensos en chunks seguros.

---

## 30. Chunk Constraints

La configuración deberá controlar:
- `maxCharactersPerChunk`
- `maxWordsPerChunk`
- `maxEstimatedDurationPerChunk`

---

## 31. Chunk Boundary

Nunca se deberá dividir una palabra. Se deberá preferir:
$$\text{sentence} > \text{clause} > \text{phrase} > \text{word}$$

---

## 32. Chunk Metadata

Cada chunk deberá conservar:

```typescript
interface TTSChunk {
  id: string;
  text: string;
  sourceStartChar: number;
  sourceEndChar: number;
  order: number;
}
```

---

## 33. Chunk Concatenation

Los chunks deberán concatenarse en orden determinista. No deberá existir silencio artificial no solicitado entre chunks.

---

## 34. Chunk Crossfade

Por defecto: $0\text{ ms}$. La unión deberá ser limpia. Si el provider produce discontinuidad, podrá aplicarse un micro-crossfade configurable.

---

## 35. Raw TTS Audio

El resultado inicial:

```typescript
interface TTSAudioResult {
  audioPath: string;
  duration: number;
  sampleRate: number;
  channels: number;
  format: string;
}
```

---

## 36. Output Format

Formato maestro:
$$\text{WAV, PCM 16-bit, Mono, 44.1 kHz}$$
compatible con el Audio Engine existente.

---

## 37. Internal Precision

Si el provider produce audio de mayor precisión (24-bit, 32-bit float, 48 kHz), la conversión deberá producirse antes del artefacto maestro.

---

## 38. Resampling

La conversión de sample rate deberá ser determinista. No deberá depender de configuración global del sistema operativo.

---

## 39. Channel Policy

La locución será `mono` por defecto.

---

## 40. Loudness Normalization

El audio deberá normalizarse según la política del Audio Engine. El TTS engine no deberá inventar niveles independientes.

---

## 41. Peak Safety

Nunca deberá generarse clipping intencional:
$$\text{peak} \le 0\text{ dBFS}$$

---

## 42. True Peak

Cuando el analizador disponible lo permita, deberá comprobarse true peak antes del export final.

---

## 43. Silence Padding

El engine no deberá añadir $1\text{s}$ de silencio al inicio o final por defecto; los offsets deberán ser metadata.

---

## 44. Voiceover Segment

```typescript
interface VoiceoverSegment {
  id: string;
  text: string;
  audioPath: string;
  start: number;
  end: number;
  duration: number;
  language: SupportedLanguage;
  voiceId: string;
}
```

---

## 45. Alignment Requirement

Cada segmento deberá disponer de timestamps provenientes de alineación nativa TTS o alineación forzada local (*local forced alignment*).

---

## 46. No Assumed TTS Timestamps

El engine nunca deberá asumir que $\text{audio duration} \approx \text{text duration}$ implica timestamps palabra por palabra.

---

## 47. Alignment Provider

```typescript
interface SpeechAligner {
  align(
    audio: AudioAsset,
    text: string,
    language: SupportedLanguage
  ): Promise<AlignmentResult>;
}
```

---

## 48. Alignment Result

```typescript
interface AlignmentResult {
  segments: AlignmentSegment[];
  words: AlignmentWord[];
}
```

---

## 49. Alignment Word

```typescript
interface AlignmentWord {
  word: string;
  start: number;
  end: number;
  confidence: number;
}
```

---

## 50. Alignment Confidence

Todos los timestamps alineados deberán conservar:
$$0.0 \le \text{confidence} \le 1.0$$

---

## 51. Alignment Failure

Si la alineación falla:
$$\text{AlignmentError}$$
El engine no deberá inventar timestamps palabra por palabra.

---

## 52. Segment Timing

La duración final será $\text{end} - \text{start}$.

---

## 53. Original Script Mapping

Cada palabra deberá poder mapearse a una posición del texto normalizado:

```typescript
interface TextWordMapping {
  normalizedStart: number;
  normalizedEnd: number;
  originalStart: number;
  originalEnd: number;
}
```

---

## 54. Localization Mapping

El sistema deberá poder conservar $\text{source sentence} \leftrightarrow \text{localized sentence} \leftrightarrow \text{localized audio}$ para futuras sincronizaciones.

---

## 55. Language Package

Cada idioma deberá producir:
- `audio_<language>.wav`
- `alignment_<language>.json`
- `script_<language>.json`

---

## 56. Voiceover Manifest

Se deberá generar `voiceover-manifest.json` con:

```typescript
interface VoiceoverManifest {
  projectId: string;
  language: SupportedLanguage;
  voiceId: string;
  provider: string;
  modelVersion: string;
  sourceTextHash: string;
  normalizedTextHash: string;
  audioHash: string;
  duration: number;
}
```

---

## 57. Hashing

El audio generado deberá disponer de hash SHA-256 para detectar cambios, corrupción o regeneraciones innecesarias.

---

## 58. Cache Key

La clave de caché mínima deberá depender de:
$$\text{sourceTextHash} + \text{language} + \text{voiceId} + \text{provider} + \text{modelVersion} + \text{TTS config} + \text{normalizerVersion}$$

---

## 59. Cache Hit

Si todos los parámetros son idénticos: `CACHE HIT` (no vuelve a sintetizarse).

---

## 60. Cache Miss

Cualquier modificación relevante deberá producir `CACHE MISS`.

---

## 61. Cache Corruption

Si el archivo cacheado no pasa validación: invalidar y regenerar.

---

## 62. Reproducibility

Misma entrada + mismo modelo + misma configuración deberá producir audio, timestamps y manifest equivalentes.

---

## 63. Determinism Caveat

Si un provider local no garantiza determinismo binario, el sistema deberá garantizar al menos determinismo semántico y registrar el hash producido.

---

## 64. Speaking Rate

`speakingRate: number` con valor neutral $1.0$.

---

## 65. Allowed Stretch

Para adaptación editorial posterior:
$$0.95\text{x} \le \text{stretch} \le 1.05\text{x}$$
será el rango inicial recomendado. El TTS no deberá aplicar automáticamente este stretch durante la generación base.

---

## 66. Pitch

El pitch deberá permanecer neutral salvo configuración explícita.

---

## 67. Voice Style

Si el provider soporta estilos (`neutral`, `narrative`, `energetic`, `calm`, `documentary`), deberán tratarse como capabilities declaradas.

---

## 68. Capability Registry

```typescript
interface VoiceCapabilities {
  supportsRate: boolean;
  supportsPitch: boolean;
  supportsStyle: boolean;
  supportsAlignment: boolean;
}
```

---

## 69. Unsupported Capability

Si se solicita una capacidad no soportada:
$$\text{UnsupportedVoiceCapabilityError}$$
No deberá ignorarse silenciosamente.

---

## 70. Language Validation

El provider deberá comprobar que la voz corresponde al idioma solicitado.

---

## 71. Cross-Language Voice

Una voz `en-US` no podrá utilizarse para `es-MX` salvo que la configuración lo permita explícitamente.

---

## 72. Translation Independence

Este módulo no será responsable de traducir; recibirá texto ya localizado:
$$\text{Translation Engine} \longrightarrow \text{MultilingualVoiceoverEngine}$$

---

## 73. Original Language

La versión original deberá conservarse como fuente (`sourceLanguage`).

---

## 74. Voiceover Variants

Un proyecto podrá contener `ES`, `EN`, `PT`, `FR`, `DE` simultáneamente como artefactos independientes.

---

## 75. Shared Narrative IDs

Las traducciones deberán conservar IDs narrativos comunes (`NARRATIVE_001`, `NARRATIVE_002`, etc.) para relacionar los segmentos en todos los idiomas.

---

## 76. Language Timing Differences

No deberá asumirse que el segmento `NARRATIVE_001` tiene igual duración en todos los idiomas:
$$\text{ES} = 4.80\text{s}, \quad \text{EN} = 3.90\text{s}, \quad \text{PT} = 4.30\text{s} \quad (\text{Todos válidos})$$

---

## 77. Audio Segment Independence

Cada idioma deberá poder generar su propio timeline, alignment, duration y pacing.

---

## 78. Integration With Adaptive Pacing

El `VlogAdaptivePacingEngine` recibirá:
$$\text{VoiceoverManifest} + \text{Narrative IDs} + \text{Original Video Timeline}$$
y decidirá cómo adaptar el montaje.

---

## 79. No Circular Dependency

`MultilingualVoiceoverEngine` no deberá depender de `VlogAdaptivePacingEngine`:
$$\text{Voiceover} \longrightarrow \text{Pacing}$$

---

## 80. Integration With Jump Cuts

La pista original podrá pasar por `VlogJumpCutEngine` antes de utilizarse como referencia editorial.

---

## 81. Voiceover Replacement

Para una versión localizada:
$$\text{Original A-roll audio} \longrightarrow \text{mute/duck} \longrightarrow \text{Localized voiceover}$$
La política será configurable.

---

## 82. Original Speaker Audio

Podrá conservarse como `AMB` o `DUCKED` según estilo.

---

## 83. Music Interaction

La música deberá continuar utilizando `Smart Audio Ducking` existente y no una segunda implementación.

---

## 84. SFX Interaction

Los SFX existentes deberán sincronizarse con el timeline adaptado.

---

## 85. Breathing

El TTS no deberá insertar respiraciones artificiales salvo que el provider las produzca naturalmente. No se deberán eliminar silencios internos del TTS automáticamente sin una política editorial.

---

## 86. Prosody Preservation

La segmentación deberá intentar conservar puntuación, pausas, estructura de oración y énfasis indicado.

---

## 87. Text Emphasis

El script podrá soportar metadata:

```typescript
interface SpeechEmphasis {
  start: number;
  end: number;
  level: number;
}
```

---

## 88. Provider That Cannot Emphasize

Si el provider no soporta emphasis: $\text{fallback} = \text{neutral prosody}$, registrando `UnsupportedVoiceCapabilityWarning`.

---

## 89. File Naming

Los archivos deberán usar nombres seguros y deterministas:
$$\text{audio\_<language>\_<voiceId>\_<hash8>.wav}$$

---

## 90. Directory Structure

```
project/
└── voiceover/
    ├── es-MX/
    │   ├── audio.wav
    │   ├── alignment.json
    │   └── manifest.json
    ├── en-US/
    ├── pt-BR/
    ├── fr-FR/
    └── de-DE/
```

---

## 91. Temporary Files

Los archivos temporales deberán almacenarse fuera del directorio final de producción.

---

## 92. Atomic Writes

Los artefactos deberán escribirse mediante estrategia segura:
$$\text{temporary file} \longrightarrow \text{validation} \longrightarrow \text{atomic rename}$$
para evitar archivos corruptos.

---

## 93. Audio Validation

Antes de aceptar un archivo:
- [ ] exists
- [ ] readable
- [ ] WAV
- [ ] PCM
- [ ] valid sample rate
- [ ] valid bit depth
- [ ] valid channels
- [ ] duration > 0
- [ ] no malformed header

---

## 94. Alignment Validation

- [ ] words ordered
- [ ] start >= 0
- [ ] end > start
- [ ] end <= audioDuration
- [ ] no impossible overlap
- [ ] confidence valid

---

## 95. Language Validation

$$\text{manifest.language} \equiv \text{requested.language}$$

---

## 96. Voice Validation

$$\text{manifest.voiceId} \equiv \text{resolved.voiceId}$$

---

## 97. Model Validation

$$\text{manifest.modelVersion} \equiv \text{actual model version}$$

---

## 98. Test — Spanish Mexico

Entrada: $\text{language} = \text{es-MX}$.  
Resultado: $\text{voice.language} = \text{es-MX}$.

---

## 99. Test — English US

Entrada: $\text{language} = \text{en-US}$.  
Resultado: $\text{voice.language} = \text{en-US}$.

---

## 100. Test — Missing Voice

Entrada: $\text{voiceId} = \text{"nonexistent"}$.  
Esperado: `VoiceNotFoundError`.

---

## 101. Test — Cache Hit

Misma entrada dos veces: la primera realiza síntesis y la segunda retorna `cache hit`.

---

## 102. Test — Cache Invalidation

Modificar una palabra: $\text{new sourceTextHash} \longrightarrow \text{cache miss}$.

---

## 103. Test — Unicode

Texto con `á`, `ñ`, `ü`, `€`, emojis: no deberá producir corrupción.

---

## 104. Test — Numbers

Texto con `1,250`, `8:42 PM`, `2026`: produce una forma lingüística válida antes del TTS.

---

## 105. Test — Chunking

Texto superior al límite configurado: genera múltiples chunks sin cortar palabras.

---

## 106. Test — Chunk Concatenation

Los chunks reconstruyen la locución en el mismo orden determinista.

---

## 107. Test — Alignment

El resultado contiene timestamps válidos para cada palabra alineada.

---

## 108. Test — Alignment Failure

Un provider de alineación que falle produce `AlignmentError`, sin inventar timestamps.

---

## 109. Test — Invalid Audio

Archivo WAV corrupto produce `AudioValidationError`.

---

## 110. Test — Unsupported Capability

Solicitar pitch a una voz que no lo soporte produce `UnsupportedVoiceCapabilityError`.

---

## 111. Property-Based Testing

Generar textos Unicode, palabras de distinta longitud, puntuación, números, idiomas, chunks, duraciones y verificar:
$$\text{no negative timestamps}, \quad \text{no invalid ranges}, \quad \text{no missing chunk order}, \quad \text{no duplicate IDs}$$

---

## 112. Fuzz Testing

Probar: `empty text`, `whitespace-only`, `very long text`, `repeated punctuation`, `malformed Unicode`, `extreme numbers`, `URLs`, `HTML`, `control characters`.

---

## 113. Security

El texto deberá tratarse como datos; no se permitirá que contenido del guion se ejecute como shell, JavaScript o ExtendScript.

---

## 114. Shell Safety

Los argumentos destinados a procesos TTS deberán pasar por APIs de ejecución segura sin concatenar texto arbitrario.

---

## 115. Resource Management

El engine deberá liberar procesos TTS, streams, buffers y archivos temporales.

---

## 116. Cancellation

La API deberá permitir cancelar una síntesis larga:

```typescript
interface VoiceoverJob {
  cancel(): Promise<void>;
}
```

---

## 117. Progress

El job podrá informar: `QUEUED`, `NORMALIZING`, `SYNTHESIZING`, `ALIGNING`, `NORMALIZING_AUDIO`, `VALIDATING`, `WRITING`, `COMPLETE`, `FAILED`, `CANCELLED`.

---

## 118. Progress Determinism

El estado del job no deberá modificar el resultado final.

---

## 119. Error Taxonomy

Errores mínimos:
- `VOICE_NOT_FOUND`
- `LANGUAGE_NOT_SUPPORTED`
- `TTS_PROVIDER_UNAVAILABLE`
- `TTS_SYNTHESIS_FAILED`
- `AUDIO_VALIDATION_FAILED`
- `ALIGNMENT_FAILED`
- `CACHE_ERROR`
- `INVALID_TEXT`
- `UNSUPPORTED_CAPABILITY`
- `RESOURCE_LIMIT`
- `CANCELLED`

---

## 120. Warning Taxonomy

- `LOW_ALIGNMENT_CONFIDENCE`
- `FALLBACK_VOICE_USED`
- `NORMALIZATION_CHANGED_TEXT`
- `UNSUPPORTED_PROSODY`
- `NONDETERMINISTIC_PROVIDER`

---

## 121. Observability

Cada generación deberá registrar: `language`, `voice`, `provider`, `model`, `duration`, `characters`, `words`, `processingTime`, `cacheHit`, `alignmentConfidence`.

---

## 122. Processing Performance

La generación podrá ejecutarse secuencial o paralelamente por idioma, manteniendo salida determinista.

---

## 123. Parallel Languages

```
ES-MX ──┐
EN-US ──┼
PT-BR ──┼──► Voiceover Package
FR-FR ──┼
DE-DE ──┘
```

---

## 124. Failure Isolation

Si FR falla, ES/EN/PT/DE podrán completarse; el proyecto marcará FR como fallido.

---

## 125. Partial Package

El manifest global deberá indicar:
- `completedLanguages`
- `failedLanguages`

---

## 126. Global Voiceover Manifest

```typescript
interface MultilingualVoiceoverManifest {
  projectId: string;
  sourceLanguage: SupportedLanguage;
  variants: VoiceoverManifest[];
  completedLanguages: SupportedLanguage[];
  failedLanguages: SupportedLanguage[];
}
```

---

## 127. Definition of Done

- [ ] Language registry definido
- [ ] Voice registry definido
- [ ] Provider abstraction definida
- [ ] Local/offline contract definido
- [ ] Text normalization definido
- [ ] Number normalization definido
- [ ] Date/time normalization definido
- [ ] Unicode definido
- [ ] Chunking definido
- [ ] TTS generation definido
- [ ] Audio format definido
- [ ] Audio normalization definido
- [ ] Alignment definido
- [ ] Word timestamps definido
- [ ] Cache definido
- [ ] Hashing definido
- [ ] Manifest definido
- [ ] Multilingual variants definido
- [ ] Shared narrative IDs definido
- [ ] Timing independence definido
- [ ] Error model definido
- [ ] Warning model definido
- [ ] Cancellation definido
- [ ] Progress definido
- [ ] Resource limits definido
- [ ] Security definido
- [ ] Tests unitarios definidos
- [ ] Property tests definidos
- [ ] Fuzz tests definidos
- [ ] Regression strategy definida
- [ ] Timeline integration definida
- [ ] Audio integration definida
- [ ] Pacing integration definida

---

## 128. Estado del documento

**Documento:** `07-MULTILINGUAL-VOICEOVER-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

Este documento define el contrato técnico del sistema de generación de voz multilingüe local. El motor de voz deberá producir únicamente artefactos de audio y alineación; la adaptación visual y temporal será responsabilidad de los módulos posteriores.
