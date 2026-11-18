# Audio & Speech Pipeline — Vlog Intelligence Engine

**Documento:** `04-AUDIO-SPEECH-PIPELINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog Multilingual Expansion  
**Objetivo:** Definir completamente la adquisición, análisis, segmentación, transcripción, sincronización, TTS y preparación de audio.  
**Dependencias:** `00-MASTER-SPECIFICATION.md`, `01-ARCHITECTURE.md`, `02-DATA-CONTRACTS.md`, `03-TEMPORAL-MODEL.md`  

---

## 1. Objetivo

Este documento define el pipeline completo:

$$\text{Audio/Video} \longrightarrow \text{Demux / Extract} \longrightarrow \text{Audio Normalization} \longrightarrow \text{VAD} \longrightarrow \text{Speech Segmentation} \longrightarrow \text{Whisper} \longrightarrow \text{Word Alignment} \longrightarrow \text{Speech Metadata} \longrightarrow \text{Editorial Silence Analysis} \longrightarrow \text{Jump-Cut Candidates} \longrightarrow \text{TTS / Localization} \longrightarrow \text{Voice Timing} \longrightarrow \text{Audio Mixing} \longrightarrow \text{AE Export}$$

Ningún módulo posterior podrá asumir información que no esté definida aquí.

---

## 2. Principio de fuente de verdad

Para el contenido hablado:
$$\text{Audio}$$
es la fuente de verdad temporal.

Whisper proporciona información lingüística. El VAD proporciona información acústica. Ninguno de los dos sustituye al otro.

---

## 3. Separación de responsabilidades

- **VAD:** Determina `SPEECH` y `NON_SPEECH`.
- **ASR / Whisper:** Determina `texto`, `segmentos`, `palabras`, `timestamps` y `confianza`.
- **Editorial Analyzer:** Determina qué silencio puede eliminarse.

Por tanto:
$$\text{VAD} \ne \text{Jump Cut Decision}$$

---

## 4. Entrada soportada

El pipeline deberá aceptar:
- WAV.
- MP3.
- AAC.
- M4A.
- MP4 con pista de audio.
- MOV con pista de audio.
- formatos adicionales soportados por el adaptador multimedia existente.

La lista definitiva dependerá del backend de ingestión disponible.

---

## 5. Audio interno canónico

Antes del análisis, el audio deberá convertirse a una representación canónica:
- **Sample Rate:** 44,100 Hz
- **Bit Depth:** 16-bit
- **Channels:** Mono
- **Encoding:** PCM

Para análisis de voz podrá utilizarse una representación interna diferente si el backend ASR/VAD lo requiere (ej. 16kHz mono). La conversión deberá ser determinista.

---

## 6. Preservación del original

El archivo fuente nunca será sobrescrito. Debe existir separación lógica:
- `source/`
- `normalized/`
- `analysis/`
- `generated/`

---

## 7. Identidad del archivo

Cada medio deberá tener un identificador estable:
```typescript
type MediaId = string;
```
El ID deberá permitir relacionar:
$$\text{source} \longrightarrow \text{audio} \longrightarrow \text{transcription} \longrightarrow \text{edit plan} \longrightarrow \text{localized audio}$$

---

## 8. Hash

Cuando sea posible, el archivo fuente deberá identificarse mediante hash criptográfico (SHA-256). El hash se utilizará para:
- cache.
- reproducibilidad.
- detección de cambios.
- invalidación.

No se deberá depender exclusivamente del nombre del archivo.

---

## 9. Cache

Las operaciones costosas deberán poder cachearse:
- decode
- normalization
- VAD
- Whisper
- word alignment
- TTS

El cache deberá invalidarse si cambia cualquiera de:
- source hash
- model
- model version
- language
- parameters
- pipeline version

---

## 10. Determinismo

Dados:
$$\text{same source} + \text{same model} + \text{same configuration} + \text{same pipeline version}$$
el resultado deberá ser reproducible dentro de las tolerancias numéricas documentadas.

---

## 11. VAD

El VAD deberá producir regiones:
```typescript
interface SpeechRegion {
  start: number;
  end: number;
  confidence: number;
}
```

---

## 12. VAD confidence

El confidence deberá estar normalizado:
$$0 \le \text{confidence} \le 1$$
Valores fuera de rango son inválidos.

---

## 13. Regiones VAD

Toda región deberá cumplir:
$$\text{start} \ge 0, \quad \text{end} > \text{start}$$

---

## 14. Regiones solapadas

Las regiones VAD superpuestas deberán normalizarse antes de enviarse al análisis editorial.

Ejemplo:
$$[1.0, 2.0) \quad \text{y} \quad [1.8, 3.0) \implies [1.0, 3.0)$$

---

## 15. Micro-regiones

Regiones extremadamente pequeñas podrán ser ruido del detector. El threshold mínimo será configurable. No se eliminarán silenciosamente sin registrar la decisión.

---

## 16. Silence Regions

Las regiones entre speech segments podrán clasificarse como:
- `SILENCE`
- `BREATH`
- `NOISE`
- `MUSIC`
- `UNKNOWN`
cuando exista información suficiente.

---

## 17. Silence ≠ Silence absoluto

El término *silencio editorial* significa:
$$\text{ausencia de habla relevante}$$
No significa necesariamente amplitud cero. Puede existir:
- ruido ambiente.
- room tone.
- respiración.
- música.
- sonido de calle.

---

## 18. Editorial Silence Candidate

Un silencio será candidato a Jump Cut cuando:
$$\text{speechBefore} + \text{nonSpeech} + \text{speechAfter}$$
formen una transición lingüísticamente segura.

---

## 19. Threshold inicial

El threshold inicial será:
$$\text{threshold} = 0.25\text{ s}$$
pero será configurable.

---

## 20. Regla de comparación

Inicialmente:
$$\text{silenceDuration} > 0.25\text{ s} \implies \text{Candidato}$$
No $\ge 0.25$.

---

## 21. Protección lingüística

Nunca deberá eliminarse una región que atraviese el intervalo de una palabra. Si existe:
$$\text{word.start} < \text{candidate.end} \quad \lor \quad \text{word.end} > \text{candidate.start}$$
el candidato deberá recortarse o rechazarse.

---

## 22. Word Timing

Cada palabra deberá representarse:
```typescript
interface WordTiming {
  id: string;
  text: string;
  start: number;
  end: number;
  confidence: number;
}
```

---

## 23. Word invariants

$$\text{start} \ge 0, \quad \text{end} > \text{start}, \quad 0 \le \text{confidence} \le 1$$

---

## 24. Texto original

El texto transcrito deberá conservarse exactamente como lo proporciona el ASR antes de cualquier normalización editorial. Se deberán separar:
- `rawText`
- `normalizedText`
- `displayText`

---

## 25. Normalización

La normalización podrá incluir:
- espacios.
- puntuación.
- casing.
- caracteres especiales.

Pero nunca deberá destruir la relación temporal con las palabras originales.

---

## 26. Idioma

Cada transcripción deberá incluir:
- `language`
- `languageConfidence`

Ejemplos: `es`, `en`, `pt`, `fr`, `de`.

---

## 27. Auto Language Detection

La detección automática podrá ejecutarse. Sin embargo, si el usuario/proyecto especifica un idioma:
$$\text{requestedLanguage}$$
tendrá prioridad.

---

## 28. Language Conflict

Si $\text{detectedLanguage} \ne \text{requestedLanguage}$, el pipeline no deberá cambiar silenciosamente de idioma. Debe registrar `LanguageMismatch` y continuar sólo si la política del proyecto lo permite.

---

## 29. Segmentos de discurso

Además de palabras, deberán existir:
```typescript
interface SpeechSegment {
  id: string;
  start: number;
  end: number;
  text: string;
  words: string[];
  confidence: number;
}
```

---

## 30. Segmentación

Los segmentos podrán dividirse por:
- pausas.
- frases.
- límites ASR.
- cambios de speaker.
- límites editoriales.

La segmentación editorial no deberá destruir el word timing.

---

## 31. Pausas

Una pausa será:
$$\text{nextWord.start} - \text{previousWord.end}$$
siempre que ambos pertenezcan al mismo contexto de discurso.

---

## 32. Breath Detection

La respiración podrá detectarse mediante análisis acústico:
```typescript
interface BreathEvent {
  start: number;
  end: number;
  confidence: number;
}
```

---

## 33. Breath Policy

La respiración no deberá eliminarse automáticamente. El sistema podrá clasificarla como:
- `KEEP`
- `OPTIONAL_REMOVE`
- `PROTECTED`

---

## 34. Protected Audio

Los siguientes elementos podrán marcarse como protegidos:
- palabra.
- nombre propio.
- frase crítica.
- reacción.
- emoción.
- información importante.
- respiración intencional.
- sonido relevante del entorno.

---

## 35. Jump-Cut Safety

Un candidato de eliminación deberá pasar:
$$\text{VAD validation} + \text{word-boundary validation} + \text{speech-segment validation} + \text{protected-event validation}$$
antes de convertirse en una instrucción de edición.

---

## 36. Resultado del análisis

El módulo deberá producir:
```typescript
interface SpeechAnalysis {
  language: string;
  segments: SpeechSegment[];
  words: WordTiming[];
  breaths: BreathEvent[];
  silenceRegions: SilenceSegment[];
  protectedRegions: TimeRange[];
}
```

---

## 37. Audio Energy

Se calculará energía/RMS por ventanas temporales. La ventana y hop deberán ser configurables.

---

## 38. RMS

El RMS se utilizará para:
- detección de energía.
- ducking.
- detección de anomalías.
- análisis editorial.

No será por sí mismo una decisión de corte.

---

## 39. Clipping

El pipeline deberá detectar muestras potencialmente saturadas:
- `clippingDetected: boolean`
- `clippingRatio: number`

---

## 40. Audio inválido

Se deberá rechazar o marcar:
- sample rate inválido.
- duración inválida.
- canales inválidos.
- archivo corrupto.
- audio ausente.
- decode incompleto.

---

## 41. Audio ausente

Si el video no contiene audio:
$$\text{AudioTrackMissing}$$
El pipeline podrá continuar únicamente en modos que no requieran voz.

---

## 42. Audio completamente silencioso

Si no existe contenido vocal detectable:
$$\text{NoSpeechDetected}$$
No deberá fabricarse una transcripción vacía como si fuese válida.

---

## 43. Whisper

Whisper será el ASR principal del pipeline inicial. La implementación deberá ser local cuando el objetivo sea:
$$\text{zero API cost, offline}$$

---

## 44. Modelo Whisper

El modelo deberá ser configurable. No se deberá hardcodear un único modelo dentro de la lógica editorial:
```typescript
interface WhisperConfig {
  model: string;
  language?: string;
  task: "transcribe" | "translate";
  device?: "cpu" | "cuda";
  precision?: "fp32" | "fp16";
}
```

---

## 45. Device

El pipeline deberá soportar, según disponibilidad:
- `CPU`
- `GPU`

La ausencia de GPU nunca deberá romper la funcionalidad.

---

## 46. Fallback

Si el backend acelerado no está disponible:
$$\text{GPU} \longrightarrow \text{CPU}$$
siempre que CPU esté soportado. El fallback deberá quedar registrado.

---

## 47. Translation vs Transcription

La tarea ASR deberá distinguir `transcribe` de `translate`. No se deberá utilizar `translate` accidentalmente para generar el texto fuente.

---

## 48. Word-Level Timing

El pipeline deberá solicitar o calcular timestamps por palabra. Los timestamps por segmento no son suficientes para Jump Cuts precisos.

---

## 49. Alineación

Si el backend ASR no proporciona word timing fiable, deberá existir una etapa explícita de alignment. No se permitirá inventar timestamps uniformemente.

---

## 50. Alignment Quality

Cada palabra deberá tener una métrica de confianza o calidad de alineación cuando esté disponible.

---

## 51. Palabras de baja confianza

Una palabra de baja confianza podrá marcarse `uncertain = true`, pero no deberá eliminarse.

---

## 52. Protección de incertidumbre

Los límites de silencio próximos a palabras inciertas deberán recibir una política conservadora.

---

## 53. Puntuación de segmento

El sistema podrá calcular:
- `speechEnergy`
- `wordDensity`
- `pauseDensity`
- `confidence`
para análisis editorial.

---

## 54. Viral Detector Integration

El `ViralMomentDetector` podrá consumir:
- words
- segments
- energy
- pacing
pero no deberá modificar la transcripción.

---

## 55. TTS

El TTS será una etapa independiente de ASR. Pipeline:
$$\text{source transcript} \longrightarrow \text{translation} \longrightarrow \text{localized text} \longrightarrow \text{TTS} \longrightarrow \text{alignment}$$

---

## 56. Idiomas iniciales

Se contemplan: `es-MX`, `es-ES`, `en-US`, `en-GB`, `pt-BR`, `fr-FR`, `de-DE`.

---

## 57. Voice Provider

El proveedor deberá ser intercambiable mediante `TTSProvider` con implementaciones locales.

---

## 58. Costo

El proveedor seleccionado para el modo offline deberá operar sin llamadas obligatorias a APIs comerciales.

---

## 59. Voice Model

La voz deberá ser configurable:
```typescript
interface VoiceConfig {
  language: string;
  voice: string;
  speed?: number;
  pitch?: number;
  style?: string;
}
```
Los campos no soportados por un backend deberán declararse como no disponibles, no fingirse.

---

## 60. TTS Output

Formato canónico:
$$\text{WAV, PCM 16-bit, 44.1 kHz, Mono}$$
salvo configuración explícita.

---

## 61. TTS Determinism

Si el motor TTS no es perfectamente determinista, el pipeline deberá guardar el artefacto generado en cache. No deberá regenerarse innecesariamente.

---

## 62. TTS Alignment

Después de generar TTS, deberá calcularse `actualDuration`. No deberá asumirse que la duración coincide con una estimación.

---

## 63. Localized Word Timing

La pista localizada deberá tener:
```typescript
interface LocalizedWordTiming {
  sourceWordId: string;
  translatedText: string;
  start: number;
  end: number;
}
```
cuando exista alineación suficiente.

---

## 64. Traducción

La traducción deberá conservar una relación semántica con el texto fuente. La traducción no deberá realizarse mediante sustitución palabra por palabra.

---

## 65. Translation Segment

Cada segmento localizado deberá conservar:
- `sourceSegmentId`
- `targetLanguage`
- `targetText`

---

## 66. TTS Duration Conflict

Si la locución supera las restricciones visuales:
$$\text{LocalizationTimingConflict}$$
deberá generarse después de intentar las estrategias permitidas.

---

## 67. Voice Stretch

El rango automático inicial será:
$$0.95\text{x} \le \text{factor} \le 1.05\text{x}$$
Fuera de ese rango se requiere estrategia adicional o error.

---

## 68. Audio Time Stretch

El time-stretch deberá preservar razonablemente:
- pitch.
- inteligibilidad.
- continuidad.
- ausencia de artefactos severos.

La implementación concreta dependerá del backend.

---

## 69. Pitch Preservation

Modificar velocidad no deberá cambiar pitch salvo que el backend no permita pitch preservation y la configuración lo autorice.

---

## 70. Voice Gain

La pista de voz deberá normalizarse según la política global del proyecto. No se deberá aplicar normalización destructiva al archivo fuente.

---

## 71. Ducking

La música podrá reducirse cuando exista voz. El ducking deberá ser controlado por:
- `voicePresence`
- `voiceEnergy`
- `attack`
- `release`
- `duckLevel`

---

## 72. Ducking Default

Los valores definitivos deberán vivir en configuración. No deberán estar dispersos por el código.

---

## 73. SFX

Los SFX podrán sincronizarse con:
- cortes.
- Punch-In.
- transiciones.
- overlays.
- Polaroid.
- eventos semánticos.

---

## 74. Audio Event

Todos los eventos deberán utilizar:
```typescript
interface AudioEvent {
  id: string;
  start: number;
  duration: number;
  asset: string;
  gain: number;
  category: "VOICE" | "MUSIC" | "SFX" | "AMBIENT";
}
```

---

## 75. Eventos fuera de rango

Un evento que quede completamente fuera del timeline deberá ser descartado (`DROP`) o generar error según su política. Nunca deberá exportarse parcialmente por accidente.

---

## 76. Mezcla

La mezcla final deberá separar conceptualmente:
- `VO`
- `MUSIC`
- `SFX`
- `AMBIENCE`

---

## 77. Prioridad de mezcla

La voz tendrá prioridad editorial sobre música. Los SFX críticos podrán superar temporalmente música, pero no deberán destruir inteligibilidad de la voz.

---

## 78. Ambient Audio

El room tone o sonido ambiente podrá utilizarse para suavizar Jump Cuts. No deberá duplicarse indefinidamente sin una regla de looping válida.

---

## 79. Micro-Crossfade

Para Jump Cuts:
$$10\text{ ms} \quad (0.010\text{ s})$$
será el valor inicial. Deberá aplicarse únicamente cuando haya material suficiente.

---

## 80. Hard Cut Fallback

Si un micro-crossfade no es posible:
$$\text{hard cut}$$
será el fallback inicial. El fallback deberá registrarse.

---

## 81. Click Prevention

Las ediciones de audio deberán evitar discontinuidades abruptas que produzcan clicks. Cuando sea posible:
$$\text{zero-crossing} + \text{micro-fade}$$
serán preferidos.

---

## 82. Audio Boundary

Cada corte deberá validar:
$$\text{source boundary} + \text{audio boundary} + \text{word boundary}$$
antes de exportarse.

---

## 83. Silence Removal Contract

El módulo editorial recibirá:
```typescript
interface SilenceCandidate {
  start: number;
  end: number;
  duration: number;
  beforeWord?: WordTiming;
  afterWord?: WordTiming;
  confidence: number;
  protection: "NONE" | "BREATH" | "WORD_MARGIN" | "MANUAL";
}
```

---

## 84. Candidate ≠ Edit

La generación de candidatos y la aplicación del corte serán módulos separados:
$$\text{Analyzer} \ne \text{Editor}$$
Esto permitirá revisar y testear las decisiones independientemente.

---

## 85. Audit Trail

Cada eliminación deberá registrar:
- `candidateId`
- `sourceRange`
- `decision`
- `reason`
- `confidence`
- `moduleVersion`

---

## 86. Decisiones posibles

- `KEEP`
- `REMOVE`
- `TRIM`
- `PROTECT`
- `REJECT`

---

## 87. Reason Codes

Ejemplos:
- `LONG_SILENCE`
- `PROTECTED_WORD`
- `LOW_CONFIDENCE`
- `BREATH`
- `INSUFFICIENT_MATERIAL`
- `TEMPORAL_CONFLICT`

---

## 88. No silent failure

Nunca se deberá descartar un candidato sin:
- `decision`
- `reason`

---

## 89. Multi-language Timeline

Cada idioma deberá tener su propia pista:
- `VO_ES`
- `VO_EN`
- `VO_PT`
- `VO_FR`
- `VO_DE`

No se deberán sobrescribir.

---

## 90. Master Timeline

El montaje visual será el master lógico. Las pistas de voz localizadas deberán adaptarse al montaje mediante el `VlogAdaptivePacingEngine`.

---

## 91. Audio Track Metadata

Cada pista deberá conservar:
- `language`
- `voice`
- `sampleRate`
- `channels`
- `duration`
- `sourceSegmentIds`

---

## 92. Missing Translation

Si un segmento no tiene traducción:
$$\text{MissingTranslation}$$
No se deberá generar TTS de texto vacío.

---

## 93. Missing Voice

Si una voz no existe para el idioma solicitado:
$$\text{VoiceUnavailable}$$
El sistema deberá detener esa variante o utilizar un fallback explícitamente configurado. Nunca deberá cambiar de idioma silenciosamente.

---

## 94. Audio Validation

Antes de exportación:
- [ ] decode válido
- [ ] sample rate válido
- [ ] duración válida
- [ ] no NaN
- [ ] no Infinity
- [ ] canales válidos
- [ ] VO presente cuando corresponde
- [ ] eventos dentro de rango
- [ ] no conflictos irresueltos

---

## 95. Tests unitarios

Deberán existir tests para:
- VAD region.
- silence threshold.
- word boundaries.
- breath detection.
- confidence.
- RMS.
- clipping.
- TTS metadata.
- duration.
- stretch limits.
- ducking.
- event scheduling.

---

## 96. Property-Based Tests

Generar aleatoriamente:
- speech regions
- silence regions
- word intervals
- audio events

y comprobar:
$$\text{start} \ge 0, \quad \text{end} > \text{start}, \quad \text{no invalid overlap}, \quad \text{no word corruption}$$

---

## 97. Test: exact threshold

Entrada: $\text{silence} = 0.250\text{s}$, $\text{threshold} = 0.250\text{s}$.  
Resultado esperado: `KEEP` con la política inicial.

---

## 98. Test: above threshold

Entrada: $\text{silence} = 0.500\text{s}$.  
Resultado esperado: `REMOVE candidate` si no existen protecciones.

---

## 99. Test: protected breath

Silencio largo + respiración protegida:
$$\text{decision} = \text{KEEP} \quad \text{o} \quad \text{TRIM}$$
según la política editorial. Nunca `REMOVE` automático.

---

## 100. Test: word crossing

Si una región candidata cruza una palabra:
$$\text{REMOVE} \implies \text{REJECT}$$
deberá rechazarse.

---

## 101. Test: localized duration

Si $\text{source} = 10.0\text{s}$ y $\text{localized} = 12.0\text{s}$: no deberá considerarse un error lingüístico; deberá enviarse al motor de pacing.

---

## 102. Test: stretch

Si la adaptación requiere $1.03\text{x}$, se permite. Si requiere $1.12\text{x}$, el auto-stretch deberá rechazarse.

---

## 103. Test: missing audio

Un archivo sin pista de audio deberá producir `AudioTrackMissing`.

---

## 104. Test: corrupted source

Un archivo no decodificable deberá producir un error estructurado. Nunca un crash no controlado.

---

## 105. Test: cache invalidation

Modificar `source hash` deberá invalidar los análisis derivados.

---

## 106. Test: language isolation

Generar ES, EN, PT deberá producir artefactos independientes. Una ejecución no deberá sobrescribir otra.

---

## 107. Test: reproducibility

Dos ejecuciones con la misma configuración deberán producir los mismos metadatos, las mismas decisiones y, cuando el backend lo permita, el mismo audio hash.

---

## 108. Errores obligatorios

El sistema deberá definir errores estructurados como mínimo:
- `AudioDecodeError`
- `AudioTrackMissing`
- `AudioFormatError`
- `NoSpeechDetected`
- `ASRError`
- `AlignmentError`
- `LanguageMismatch`
- `MissingTranslation`
- `VoiceUnavailable`
- `TTSError`
- `TTSAlignmentError`
- `LocalizationTimingConflict`
- `AudioMixError`

---

## 109. Logging

Cada etapa deberá registrar:
- `pipelineRunId`
- `mediaId`
- `stage`
- `duration`
- `status`
- `warnings`
- `errors`

No deberá registrarse audio binario en logs.

---

## 110. Seguridad de archivos

Las rutas de entrada/salida deberán validarse. No se deberá permitir que nombres de archivos o metadata controlen rutas arbitrarias fuera del workspace autorizado.

---

## 111. Recursos

Las operaciones pesadas deberán poder controlar:
- `CPU`
- `RAM`
- `GPU`
- `disk`

Los límites deberán ser configurables.

---

## 112. Cancelación

Cada etapa larga deberá poder recibir una señal de cancelación. Una cancelación no deberá dejar el pipeline marcado como exitoso.

---

## 113. Reanudación

Cuando sea posible, las etapas completadas deberán reutilizarse desde cache.

---

## 114. Estado del Pipeline

Estados:
- `PENDING`
- `RUNNING`
- `COMPLETED`
- `FAILED`
- `CANCELLED`

---

## 115. Artefactos

El pipeline deberá producir como mínimo:
- `normalized.wav`
- `vad.json`
- `transcript.json`
- `speech-analysis.json`
- `audio-analysis.json`

y, para localización:
- `translation_<lang>.json`
- `audio_<lang>.wav`
- `alignment_<lang>.json`

---

## 116. Contrato final

El resultado deberá poder alimentar directamente:
- `VlogJumpCutEngine`
- `VlogAdaptivePacingEngine`
- `MultilingualVoiceoverEngine`
- `VlogFootageClassifier`
- `SocialLaunchPackager`
- `AfterEffectsExporter`

sin que estos módulos tengan que volver a analizar el audio.

---

## 117. Definition of Done

- [ ] Ingestión definida
- [ ] Audio canónico definido
- [ ] Cache definido
- [ ] Determinismo definido
- [ ] VAD definido
- [ ] Silence analysis definido
- [ ] Word timing definido
- [ ] Speech segments definidos
- [ ] Breath detection definido
- [ ] Protected regions definido
- [ ] Whisper definido
- [ ] Alignment definido
- [ ] Confidence definido
- [ ] Language handling definido
- [ ] Translation contract definido
- [ ] TTS contract definido
- [ ] Localized timing definido
- [ ] Voice stretch definido
- [ ] Ducking definido
- [ ] SFX definido
- [ ] Audio events definido
- [ ] Micro-crossfade definido
- [ ] Hard-cut fallback definido
- [ ] Audit trail definido
- [ ] Errors definidos
- [ ] Logging definido
- [ ] Cache invalidation definido
- [ ] Tests definidos
- [ ] Property tests definidos
- [ ] Edge cases definidos

---

## 118. Estado del documento

**Documento:** `04-AUDIO-SPEECH-PIPELINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

La implementación deberá comenzar únicamente cuando este contrato y sus dependencias hayan sido aprobados.
