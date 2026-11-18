# Multilingual Subtitle Engine

**Documento:** `10-MULTILINGUAL-SUBTITLE-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog Multilingual Expansion  
**Dependencias:** `LocalWhisperTranscriptionBridge`, Typography Engine, Timeline Engine, Localization Engine, `VlogAdaptivePacingEngine`, `VlogTravelOverlaysEngine`, Reframing Engine, After Effects JSX Exporter  

---

## 1. Objetivo

Definir completamente el motor responsable de generar, sincronizar, localizar, diseñar y exportar subtítulos para Vlogs, documentales, Shorts y contenido multilingüe.

El sistema deberá soportar:
- transcripción palabra por palabra;
- timestamps por palabra;
- segmentación automática;
- subtítulos por frase;
- karaoke palabra por palabra;
- múltiples idiomas;
- múltiples pistas de voz;
- traducción mediante texto previamente localizado;
- adaptación a diferencias de duración entre idiomas;
- emojis;
- signos de puntuación;
- grafemas Unicode complejos;
- estilos virales;
- safe zones;
- detección de colisiones;
- reflow responsive;
- 16:9, 9:16, 1:1, 4:5, 21:9;
- exportación a After Effects;
- validación determinista;
- pruebas unitarias y property-based.

---

## 2. Principio Arquitectónico

El Subtitle Engine no deberá generar subtítulos directamente desde una cadena de texto. El flujo obligatorio será:

$$\text{Audio Track} \longrightarrow \text{Word Alignment} \longrightarrow \text{Transcript Model} \longrightarrow \text{Sentence Segmentation} \longrightarrow \text{Subtitle Segmentation} \longrightarrow \text{Readability Validation} \longrightarrow \text{Localization} \longrightarrow \text{Typography Layout} \longrightarrow \text{Safe-Zone / Collision Resolution} \longrightarrow \text{Animation} \longrightarrow \text{Timeline Layers} \longrightarrow \text{After Effects JSX}$$

---

## 3. Fuente de Verdad

La unidad fundamental será `SubtitleDocument`. No deberá utilizarse el texto visual como fuente primaria de sincronización.

---

## 4. Supported Languages

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
La arquitectura deberá permitir añadir idiomas posteriormente sin modificar el núcleo del motor.

---

## 5. Language Metadata

```typescript
interface LanguageMetadata {
  language: SupportedLanguage;
  direction: "LTR" | "RTL";
  defaultReadingSpeedWpm: number;
  defaultWordsPerSubtitle: number;
  defaultMaxLines: number;
}
```

---

## 6. Subtitle Document

```typescript
interface SubtitleDocument {
  id: string;
  schemaVersion: string;
  language: SupportedLanguage;
  sourceTrackId: string;
  segments: SubtitleSegment[];
  metadata: SubtitleMetadata;
}
```

---

## 7. Subtitle Metadata

```typescript
interface SubtitleMetadata {
  createdAt?: string;
  sourceTranscriptId: string;
  localizationSourceId?: string;
  voiceTrackId?: string;
  version: string;
}
```
Los timestamps internos del motor deberán ser deterministas.

---

## 8. Word Token

La unidad mínima será:

```typescript
interface SubtitleWord {
  id: string;
  text: string;
  normalizedText: string;
  start: number;
  end: number;
  confidence?: number;
  punctuationBefore?: string;
  punctuationAfter?: string;
}
```

---

## 9. Word Timing Invariant

Siempre:
$$\text{end} > \text{start}, \quad \text{start} \ge 0$$

---

## 10. Word Overlap

Dos palabras consecutivas de la misma pista no deberán solaparse salvo que el modelo de alineación explícitamente lo permita.

---

## 11. Transcript Segment

```typescript
interface TranscriptSegment {
  id: string;
  words: SubtitleWord[];
  start: number;
  end: number;
  text: string;
}
```

---

## 12. Subtitle Segment

```typescript
interface SubtitleSegment {
  id: string;
  text: string;
  words: SubtitleWord[];
  start: number;
  end: number;
  lineCount: number;
  readingSpeed: number;
}
```

---

## 13. Subtitle Timing

El segmento deberá cumplir:
$$\text{start} = \text{firstWord.start}, \quad \text{end} = \text{lastWord.end}$$
salvo que exista una extensión explícita de display.

---

## 14. Display Padding

```typescript
interface DisplayPadding {
  before: number; // 0.03s por defecto
  after: number;  // 0.08s por defecto
}
```

---

## 15. Maximum Duration

$$\text{maxDuration} = 6.0\text{ s}$$

---

## 16. Minimum Duration

$$\text{minDuration} = 0.60\text{ s}$$

---

## 17. Minimum Duration Conflict

Si una frase dura menos que el mínimo: intentar extender hacia silencio, comprobar colisión con el siguiente segmento o dividir; nunca crear solapamiento silencioso.

---

## 18. Maximum Characters

```typescript
interface SubtitleLimits {
  maxCharactersPerLine: number; // 42 para horizontal
  maxLines: number;             // 2
  maxCharactersTotal: number;
}
```

---

## 19. Vertical Format

Para 9:16:
$$\text{maxCharactersPerLine} = 30, \quad \text{maxLines} = 2$$

---

## 20. Words Per Subtitle

Por defecto $2\text{ a }7\text{ palabras}$; el motor decidirá mediante puntuación, duración y ancho visual.

---

## 21. Segmentation Priority

$$\text{Puntuación fuerte} > \text{Pausa natural} > \text{Unidad semántica} > \text{Ancho visual} > \text{Velocidad de lectura} > \text{Número de palabras}$$

---

## 22. Punctuation Boundaries

Preferir cortes después de `.`, `?`, `!`, `:`, `;` antes que dividir arbitrariamente una oración.

---

## 23. Weak Boundaries

Podrán utilizarse `,`, `—`, conjunciones o respiraciones naturales cuando sea necesario.

---

## 24. Never Split

Evitar separar: `nombre + apellido`, `número + unidad`, `símbolo + número`, `palabra + porcentaje`.

---

## 25. Reading Speed

$$\text{WPM} = \frac{\text{words}}{\text{durationMinutes}}$$

---

## 26. Reading Speed Limits

- $\text{minimum} = 90\text{ WPM}$
- $\text{comfortable} = 150\text{--}180\text{ WPM}$
- $\text{maximum} = 220\text{ WPM}$

---

## 27. Viral Subtitle Mode

Presets como Hormozi/MrBeast podrán utilizar segmentos cortos, alto énfasis y animación a nivel de palabra respetando los límites mínimos de legibilidad.

---

## 28. Karaoke Model

```typescript
interface KaraokeWordState {
  wordId: string;
  state: "UPCOMING" | "ACTIVE" | "COMPLETED";
  progress: number;
}
```

---

## 29. Karaoke Progress

$\text{progress} = 0$ al inicio y $\text{progress} = 1$ al finalizar la palabra.

---

## 30. Word-Level Highlight

El highlight se calculará usando timestamps reales, no divisiones uniformes.

---

## 31. Active Word

En cualquier instante $t$:
$$\text{word.start} \le t < \text{word.end} \implies \text{palabra activa}$$

---

## 32. Punctuation Handling

La puntuación debe permanecer visualmente asociada a la palabra correspondiente (`Hola,` nunca en dos líneas).

---

## 33. Unicode

El engine operará por grafemas (`Intl.Segmenter`); nunca asumir `string.length` como número de caracteres visuales.

---

## 34. Grapheme Segmentation

Compatible con Unicode Grapheme Cluster Boundaries.

---

## 35. Emoji

Un emoji (🔥) se trata como unidad visual indivisible.

---

## 36. Combining Marks

Preservar correctamente marcas combinantes (`é`, `ñ`, `ü`, `á`).

---

## 37. Ligatures

Composición delegada al `Typography Engine` existente de v3.4.0.

---

## 38. Font Selection

```typescript
interface SubtitleFontConfig {
  primary: string;
  fallback: string[];
}
```

---

## 39. Missing Font

$$\text{Primary} \longrightarrow \text{Fallback 1} \longrightarrow \text{Fallback 2} \longrightarrow \text{System fallback} \implies \text{FONT\_FALLBACK\_USED}$$

---

## 40. Layout Model

```typescript
interface SubtitleLayout {
  anchor: OverlayAnchor;
  x: number;
  y: number;
  maxWidth: number;
  maxHeight: number;
  scale: number;
  rotation: number;
}
```

---

## 41. Normalized Coordinates

$$x \in [0, 1], \quad y \in [0, 1]$$

---

## 42. Subtitle Safe Zone

La posición final respetará `SafeArea` proporcionada por el Reframing Engine.

---

## 43. Platform Safe Zones

Presets: `YOUTUBE`, `SHORTS`, `TIKTOK`, `REELS`, `GENERIC`.

---

## 44. Subtitle Vertical Priority

Posición por defecto: `bottom-center`, desplazándose automáticamente ante colisiones con UI, rostros o lower-thirds.

---

## 45. Collision Detection

```typescript
interface OccupiedRegion {
  x: number;
  y: number;
  width: number;
  height: number;
  priority: number;
  source: string;
}
```

---

## 46. Collision Resolution

$$\text{Mover} \longrightarrow \text{Compactar} \longrightarrow \text{Reducir escala} \longrightarrow \text{Aumentar líneas} \longrightarrow \text{Ocultar elementos secundarios}$$
(Nunca ocultar subtítulos primarios).

---

## 47. Face Collision

Si el rostro ocupa la posición inferior central, el subtítulo se mueve hacia `bottom-left`, `bottom-right` o `middle-lower`.

---

## 48. Subject Protection

El sujeto principal tiene prioridad visual sobre el subtítulo; el subtítulo busca una región alternativa sin desaparecer.

---

## 49. Subtitle Background

```typescript
type SubtitleBackground =
  | "NONE"
  | "BOX"
  | "ROUNDED_BOX"
  | "PILL"
  | "SHADOW"
  | "STROKE"
  | "GLOW";
```

---

## 50. Text Color

```typescript
interface SubtitleColor {
  base: ColorRGBA;
  active?: ColorRGBA;
  completed?: ColorRGBA;
}
```

---

## 51. Karaoke Color

Ejemplo: `base = white`, `active = yellow`.

---

## 52. Word Emphasis

```typescript
interface WordEmphasis {
  scale?: number;
  color?: ColorRGBA;
  weight?: number;
  glow?: boolean;
  pop?: boolean;
}
```

---

## 53. Emphasis Detection

Recibirá `EmphasisScore` desde el `ViralMomentDetector`.

---

## 54. Emphasis Priority

$$\text{explicit emphasis} > \text{viral detector} > \text{punctuation} > \text{default}$$

---

## 55. Number Emphasis

Números importantes (`100%`, `$1,000`, `3 días`) podrán resaltarse.

---

## 56. Proper Noun Emphasis

Nombres propios podrán resaltarse mediante entidades verificadas.

---

## 57. Subtitle Style

```typescript
interface SubtitleStyle {
  font: SubtitleFontConfig;
  color: SubtitleColor;
  background: SubtitleBackground;
  stroke?: StrokeStyle;
  shadow?: ShadowStyle;
  emphasis?: WordEmphasis;
  alignment: ParagraphJustification;
}
```

---

## 58. Existing Style Presets

Reutilizar presets existentes: `Hormozi`, `MrBeast`, `TIME`, `Minimalist Kinetic`, `Cinematic Travel`, `Documentary`, `Vox`.

---

## 59. Style Override

```typescript
styleOverride?: Partial<SubtitleStyle>;
```

---

## 60. Language-Specific Style

El estilo podrá variar por idioma únicamente cuando sea necesario; la geometría se mantiene equivalente.

---

## 61. Translation Alignment

```typescript
interface TranslationBinding {
  sourceSegmentId: string;
  targetSegmentId: string;
}
```

---

## 62. Word Translation Alignment

```typescript
interface WordAlignment {
  sourceWordId: string;
  targetWordId?: string;
  confidence?: number;
}
```

---

## 63. Multi-Language Timing

Cada idioma tiene sus propios timestamps; prohibido copiar ciegamente el timing de la fuente.

---

## 64. Voice Track Binding

```typescript
interface SubtitleVoiceBinding {
  language: SupportedLanguage;
  voiceTrackId: string;
}
```

---

## 65. Timing Source Priority

1. Target-language voice alignment
2. Localized narration timing
3. Adapted source timing

---

## 66. Original Audio Mode

Si no existe voz localizada, la voz original se utiliza como fuente temporal.

---

## 67. TTS Timing

$$\text{audio} \longrightarrow \text{forced alignment} \longrightarrow \text{word timestamps} \longrightarrow \text{subtitle}$$

---

## 68. Whisper Alignment

El resultado de Whisper se normaliza al modelo interno.

---

## 69. Confidence

$$\text{confidence} \in [0, 1]$$

---

## 70. Low Confidence

Si $\text{confidence} < \text{threshold} \implies \text{LOW\_TRANSCRIPTION\_CONFIDENCE}$.

---

## 71. Human Review Flag

Segmentos críticos podrán marcarse con `requiresReview: boolean`.

---

## 72. Automatic Correction

No alterar silenciosamente palabras dudosas; registrar toda corrección.

---

## 73. Correction Model

```typescript
interface TranscriptCorrection {
  original: string;
  corrected: string;
  reason: string;
  confidence: number;
}
```

---

## 74. Timing Drift

El engine detectará desviaciones entre el timeline de subtítulos y el de audio.

---

## 75. Drift Threshold

$\text{Drift} \ge 50\text{ ms} \implies \text{warning}$.

---

## 76. Critical Drift

$\text{Drift} \ge 150\text{ ms} \implies \text{error de validación en segmentos críticos}$.

---

## 77. Subtitle Gap

Sin gaps accidentales entre segmentos de una misma frase.

---

## 78. Subtitle Overlap

Dos segmentos de la misma pista no podrán solaparse.

---

## 79. Natural Gap

Separación mínima natural de $20\text{--}80\text{ ms}$.

---

## 80. Breathing Alignment

Recibe eventos `BreathPause` desde `VoiceoverTimingSynchronizer`.

---

## 81. Pause-Aware Segmentation

Una pausa $\ge 0.30\text{s}$ es un punto natural de corte.

---

## 82. Long Sentence Strategy

$$\text{semantic split} \longrightarrow \text{pause split} \longrightarrow \text{punctuation split} \longrightarrow \text{visual split}$$

---

## 83. Line Breaking

Optimiza legibilidad, agrupación semántica y balance visual.

---

## 84. Center Alignment

`ParagraphJustification.CENTER_JUSTIFY` por defecto.

---

## 85. Orphan Prevention

Evitar palabras huérfanas en líneas separadas.

---

## 86. Widow Prevention

Evitar palabras viudas al final de párrafos.

---

## 87. Dynamic Font Scaling

Reducción incremental ($\times 0.95$) sin bajar del tamaño mínimo.

---

## 88. Minimum Font Size

`minimumFontSize: number` relativo a la resolución y formato.

---

## 89. Subtitle Animation

```typescript
interface SubtitleAnimation {
  entrance: AnimationPreset;
  wordActive?: AnimationPreset;
  exit: AnimationPreset;
}
```

---

## 90. Default Animation

Subtítulos normales: `FADE`; Karaoke: `WORD_HIGHLIGHT`.

---

## 91. Animation Boundary

Las animaciones deben permanecer dentro del intervalo del segmento.

---

## 92. Word Pop

El efecto POP no debe alterar permanentemente el layout de las palabras vecinas (transformación local).

---

## 93. Karaoke Rendering Strategies

`COLOR_FILL`, `SCALE`, `BACKGROUND_HIGHLIGHT`, `UNDERLINE`, `GLOW`.

---

## 94. Subtitle Layer Strategy

En After Effects: capa de texto única con animadores, o capas por palabra cuando el preset lo exija.

---

## 95. Default AE Strategy

Capa de texto única (`ADBE Text Document`) con animadores para máxima eficiencia.

---

## 96. Word-Layer Strategy

Utilizada para presets de alta dispersión espacial o énfasis individual complejo.

---

## 97. Layer Naming

$$\text{VLOG\_SUB\_<LANG>\_<SEGMENT\_ID>}$$
Ejemplo: `VLOG_SUB_ES-MX_SEG_0042`.

---

## 98. Word Layer Naming

$$\text{VLOG\_SUB\_<LANG>\_<SEGMENT\_ID>\_WORD\_<INDEX>}$$

---

## 99. AE Metadata

Contiene: `subtitleId`, `language`, `segmentId`, `voiceTrackId`, `schemaVersion`.

---

## 100. JSX Localization Safety

Uso exclusivo de Match Names universales.

---

## 101. Export Formats

Formatos maestros: `JSON` y `AE JSX`. Exportación a `SRT` y `VTT` mediante adaptadores.

---

## 102. SRT

El adaptador SRT preserva únicamente la información soportada por el estándar SRT.

---

## 103. VTT

Adaptador VTT con mapeo de cues y posicionamiento.

---

## 104. Subtitle Hash

$$\text{hash}(\text{text} + \text{timing} + \text{style} + \text{language})$$

---

## 105. Cache

Caché de layout, segmentación y estilo resuelto.

---

## 106. Cache Invalidation

Se invalida al cambiar texto, timing, idioma, fuente, estilo, canvas o safe zone.

---

## 107. Determinism

Misma entrada genera idénticos segmentos, saltos de línea, posiciones y animación.

---

## 108. Random

Prohibido `Math.random()`.

---

## 109. Seed

$$\text{seed} = \text{projectSeed} + \text{subtitleId}$$

---

## 110. Validation API

```typescript
validateSubtitleDocument(document: SubtitleDocument): ValidationResult
```

---

## 111. Validation Rules

Comprobar schema, idioma, IDs, timings, solapamientos, duraciones, safe zones y vinculación de voz.

---

## 112. Error Types

```typescript
type SubtitleError =
  | "InvalidSubtitleTimingError"
  | "SubtitleOverlapError"
  | "SubtitleDurationError"
  | "SubtitleLayoutError"
  | "UnsupportedLanguageError"
  | "MissingVoiceTrackError"
  | "SubtitleCollisionError"
  | "InvalidWordTimingError"
  | "SubtitleTextOverflowError";
```

---

## 113. Warnings

- `LOW_TRANSCRIPTION_CONFIDENCE`
- `LOW_READING_SPEED`
- `HIGH_READING_SPEED`
- `FONT_FALLBACK_USED`
- `TEXT_COMPACTED`
- `SUBTITLE_REPOSITIONED`
- `SUBTITLE_LINE_REFLOW`
- `TIMING_DRIFT`
- `AUTO_CORRECTION_APPLIED`

---

## 114. Property-Based Testing

Generar textos, palabras, timings, puntuación, emojis y formatos, verificando invariantes.

---

## 115. Timing Property

$$0 \le \text{start} < \text{end}$$

---

## 116. Segment Property

$$\text{segment.start} \le \text{firstWord.start}, \quad \text{segment.end} \ge \text{lastWord.end}$$

---

## 117. Overlap Property

$$\text{segment}[i].\text{end} \le \text{segment}[i+1].\text{start}$$

---

## 118. Reading Property

Si el segmento supera el límite WPM, debe dividirse si existe un punto de corte válido.

---

## 119. Unicode Property

Serializar y deserializar no modifica grafemas, emojis ni puntuación.

---

## 120. Layout Property

Todo texto obligatorio permanece dentro de `canvas + safe area`.

---

## 121. Collision Property

Un subtítulo nunca ocupa una región marcada como `forbidden = true`.

---

## 122. Karaoke Property

En cualquier instante $t$ existe como máximo una palabra activa por stream.

---

## 123. Multi-Language Property

Cada idioma conserva su mapeo semántico de segmentos.

---

## 124. Translation Property

Una traducción no modifica accidentalmente `sourceSegmentId`.

---

## 125. Golden Test

`golden_multilingual_subtitles.json` con ES-MX, EN-US, PT-BR, FR-FR, DE-DE sobre la misma secuencia.

---

## 126. Golden Assertions

Comparar conteo de segmentos, palabras, timestamps, saltos de línea, estilos y posiciones.

---

## 127. Integration Test

$$\text{Whisper} \longrightarrow \text{Transcript} \longrightarrow \text{Localization} \longrightarrow \text{TTS} \longrightarrow \text{Word Alignment} \longrightarrow \text{Subtitle Segmentation} \longrightarrow \text{Layout} \longrightarrow \text{Safe Zones} \longrightarrow \text{AE JSX}$$

---

## 128. Performance

Procesamiento de piezas de $60\text{ minutos}$ sin requerir After Effects durante el cálculo.

---

## 129. Batch

Capaz de generar simultáneamente los 7 idiomas para una misma producción.

---

## 130. CLI

```bash
npm run vlog:subtitles
```

---

## 131. Language Selection

```bash
npm run vlog:subtitles -- --languages es-MX,en-US,pt-BR
```

---

## 132. Dry Run

```bash
npm run vlog:subtitles -- --dry-run
```
produce `subtitle-plan.json` sin generar JSX final.

---

## 133. Debug Mode

```bash
npm run vlog:subtitles -- --debug
```

---

## 134. Logging

Registra: `documentId`, `language`, `sourceTrack`, `voiceTrack`, `segmentCount`, `wordCount`, `warnings`, `errors`, `duration`.

---

## 135. Idempotency

Misma entrada genera idéntico documento.

---

## 136. Recovery

Fallo parcial en un idioma (ej. PT) no destruye los idiomas completados (ES, EN, FR).

---

## 137. Failure Policy

Default: `skip + report` para permitir producción parcial.

---

## 138. Security / Input Safety

Texto tratado estrictamente como datos sin ejecución de código.

---

## 139. JSX Escaping

Escape riguroso de comillas, barras, saltos de línea y caracteres Unicode en JSX.

---

## 140. Maximum Subtitle Count

Soporte de miles de segmentos sin cuelgues de memoria.

---

## 141. Memory

Procesamiento por chunks/streaming para documentos masivos.

---

## 142. Schema Version

$$\text{schemaVersion} = \text{"1.0.0"}$$

---

## 143. Migration

Estrategia formal de migración ante cambios de esquema.

---

## 144. Observability

Rastreabilidad total:
$$\text{audio} \longrightarrow \text{word} \longrightarrow \text{segment} \longrightarrow \text{subtitle layer} \longrightarrow \text{AE layer}$$

---

## 145. Trace ID

```typescript
interface SubtitleTrace {
  sourceTrackId: string;
  transcriptId: string;
  segmentId: string;
  layerId?: string;
}
```

---

## 146. Definition of Done

- [ ] SubtitleDocument definido
- [ ] SubtitleSegment definido
- [ ] SubtitleWord definido
- [ ] Word timing definido
- [ ] Segmentación definida
- [ ] Límites de lectura definidos
- [ ] Límites de duración definidos
- [ ] Punctuation boundaries definidos
- [ ] Unicode definido
- [ ] Grapheme handling definido
- [ ] Emoji handling definido
- [ ] Karaoke definido
- [ ] Word emphasis definido
- [ ] Multi-language definido
- [ ] Translation binding definido
- [ ] Voice binding definido
- [ ] TTS timing definido
- [ ] Whisper alignment definido
- [ ] Confidence definido
- [ ] Correction model definido
- [ ] Timing drift definido
- [ ] Safe zones definido
- [ ] Collision detection definido
- [ ] Face avoidance definido
- [ ] Responsive layout definido
- [ ] Aspect ratios definidos
- [ ] Typography integration definida
- [ ] Font fallback definido
- [ ] Style presets definidos
- [ ] Animation definida
- [ ] AE layer strategy definida
- [ ] JSX escaping definido
- [ ] SRT/VTT adapters definidos
- [ ] Cache definido
- [ ] Cache invalidation definido
- [ ] Determinism definido
- [ ] Validation definido
- [ ] Errors definidos
- [ ] Warnings definidos
- [ ] Property-based tests definidos
- [ ] Golden tests definidos
- [ ] Integration tests definidos
- [ ] CLI definido
- [ ] Dry-run definido
- [ ] Debug definido
- [ ] Logging definido
- [ ] Idempotency definido
- [ ] Partial failure definido
- [ ] Recovery definido
- [ ] Schema version definido
- [ ] Migration definido
- [ ] Traceability definida

---

## 147. Estado Final del Documento

**Documento:** `10-MULTILINGUAL-SUBTITLE-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

Este documento establece que el sistema de subtítulos será independiente del idioma, sincronizado con la pista de voz real, Unicode-safe, responsive, determinista y compatible con el sistema tipográfico existente. No se permitirá que After Effects decida automáticamente segmentación, timing, idioma, safe zones o reglas de legibilidad que deban haber sido determinadas previamente por el motor.
