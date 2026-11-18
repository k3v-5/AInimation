# Vlog Adaptive Pacing Engine

**Archivo:** `18-VLOG-ADAPTIVE-PACING-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  
**Dependencias:** Documentos 1–17  
**Consumidores:** Timeline Engine, VlogJumpCutEngine, B-Roll Matcher, Subtitle Engine, Audio Engine, After Effects JSX Exporter  

---

## 1. Objetivo

Definir el sistema responsable de adaptar automáticamente una edición audiovisual a la duración real de una locución en cada idioma.

El motor deberá resolver:
$$\text{guion localizado} + \text{duración de voz} + \text{timings de palabras} + \text{segmentos visuales} + \text{puntos narrativos} \implies \text{timeline adaptado por idioma}$$

El resultado conservará: intención narrativa, orden de escenas, sincronización de voz, legibilidad de subtítulos, puntos de énfasis, duración visual razonable, continuidad y ritmo de vlog/documental.

---

## 2. Principio Fundamental

El sistema no deberá asumir que una traducción tiene la misma duración que el idioma original:
$$\text{timeline\_base} \ne \text{timeline\_localizado}$$
Cada idioma poseerá su propio timeline derivado.

---

## 3. Arquitectura

```
                    SOURCE TIMELINE
                          │
                          ▼
                 NARRATIVE SEGMENTS
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       VISUAL SEGMENTS          VOICEOVER PACKAGE
                                      │
                                      ▼
                              WORD / PHRASE TIMINGS
                                      │
                                      ▼
                         ADAPTIVE PACING ENGINE
                                      │
             ┌────────────────────────┼──────────────────────┐
             ▼                        ▼                      ▼
       Extend Visuals           Compress Visuals       Time-Stretch Voice
             │                        │                      │
             └────────────────────────┼──────────────────────┘
                                      ▼
                              CONFLICT RESOLUTION
                                      │
                                      ▼
                              LOCALIZED TIMELINE
```

---

## 4. Unidad Fundamental

La unidad de adaptación será el `NarrativeSegment`. Prohibido editar basándose exclusivamente en fotogramas individuales sin contexto semántico.

---

## 5. Narrative Segment

```typescript
interface NarrativeSegment {
  id: string;
  order: number;
  sourceStart: number;
  sourceEnd: number;
  sourceDuration: number;
  textSegmentId: string;
  visualPlan: VisualPlan;
  importance: SegmentImportance;
  timingPolicy: TimingPolicy;
}
```

---

## 6. Segment Importance

```typescript
type SegmentImportance =
  | "CRITICAL"
  | "HIGH"
  | "NORMAL"
  | "LOW";
```

---

## 7. Significado

- `CRITICAL`: Intocable temporalmente (punchlines, revelaciones, datos clave, hook inicial, CTA).
- `HIGH`: Modificaciones mínimas toleradas.
- `NORMAL`: Extensión o compresión dentro de tolerancias estándar.
- `LOW`: Principal absorbedor elástico de deltas de tiempo.

---

## 8. Timing Policy

```typescript
interface TimingPolicy {
  minDuration: number;
  preferredDuration: number;
  maxDuration: number;
  allowExtension: boolean;
  allowCompression: boolean;
  allowTimeStretch: boolean;
  allowBrollSwap: boolean;
}
```

---

## 9. Duration Constraints

$$\text{minDuration} \le \text{actualDuration} \le \text{maxDuration}$$

---

## 10. Flexible Segments

```typescript
type SegmentFlexibility =
  | "FIXED"
  | "CONSTRAINED"
  | "FLEXIBLE";
```

---

## 11. Fixed Segment

Invariable temporalmente (intros musicales, animaciones de logotipo, transiciones complejas o patrocinios).

---

## 12. Constrained Segment

Adaptación acotada dentro de límites estrechos.

---

## 13. Flexible Segment

Tomas de paisaje, B-Roll de caminata, planos de establecimiento o ambiente urbano.

---

## 14. Voice Is Primary

$$\text{VOICE} = \text{Autoridad temporal principal}$$
La edición visual se adapta preferentemente a la cadencia de la locución.

---

## 15. Exception

Elementos visuales marcados como `FIXED_EVENT` actúan como anclas maestras (impactos, aperturas de puertas, match cuts, drops musicales).

---

## 16. Timing Anchors

```typescript
interface TimingAnchor {
  id: string;
  type:
    | "WORD"
    | "PHRASE"
    | "BEAT"
    | "VISUAL_EVENT"
    | "MUSIC_EVENT"
    | "CTA";
  time: number;
  priority: number;
}
```

---

## 17. Anchor Priority

$$\text{CRITICAL VISUAL EVENT} > \text{CRITICAL NARRATIVE PHRASE} > \text{CTA} > \text{MUSIC EVENT} > \text{NORMAL PHRASE} > \text{AMBIENT BEAT}$$

---

## 18. Voice Timings

Consumo obligatorio de `VoiceWordTiming[]` emitidos por el motor de locución.

---

## 19. Phrase Boundaries

```typescript
interface PhraseTiming {
  id: string;
  wordStartIndex: number;
  wordEndIndex: number;
  start: number;
  end: number;
  importance: SegmentImportance;
}
```

---

## 20. Pause-Aware Editing

Las pausas naturales de la voz son los puntos idóneos para cortes, cambios de B-Roll, punch-ins y respiración visual.

---

## 21. Pause Threshold

Pausa editorial básica: $\text{duración} \ge 0.20\text{ s}$.

---

## 22. Strong Pause

Pausa fuerte: $\text{duración} \ge 0.50\text{ s}$ (oportunidad mayor de transición).

---

## 23. Micro Pause

Pausas $< 0.20\text{ s}$ no provocan cortes de plano automáticos.

---

## 24. Language Expansion

Comparación sistemática de la duración localizada frente a la fuente.

---

## 25. Duration Delta

$$\Delta = \text{localizedDuration} - \text{sourceDuration}$$

---

## 26. Delta Ratio

$$\text{ratio} = \frac{\text{localizedDuration}}{\text{sourceDuration}}$$

---

## 27. Ejemplo

$$\text{source} = 10.0\text{ s}, \quad \text{localized} = 12.0\text{ s} \implies \Delta = +2.0\text{ s}, \; \text{ratio} = 1.20$$

---

## 28. No Hardcode Language Expansion

Prohibido asumir porcentajes de expansión rígidos por idioma (ej. español $+20\%$). La duración real de la locución es la verdad absoluta.

---

## 29. Language Statistics

```typescript
interface LanguagePacingStatistics {
  language: LanguageCode;
  averageExpansionRatio: number;
  sampleCount: number;
}
```
Métricas puramente predictivas; nunca sustituyen al audio real.

---

## 30. Adaptation Strategies

Orden de resolución:
1. Ajustar espacios flexibles
2. Extender B-Roll
3. Intercambiar B-Roll compatible
4. Redistribuir duración entre segmentos
5. Time-stretch suave de voz
6. Compresión visual controlada
7. Fallback editorial

---

## 31. Strategy Budget

```typescript
interface AdaptationBudget {
  extensionSeconds: number;
  compressionSeconds: number;
  maxVoiceStretch: number;
  maxVoiceCompression: number;
}
```

---

## 32. B-Roll Extension

Extensión mediante fotograma congelado (*freeze*), tomas alternativas, bucles o cámara lenta cinemática.

---

## 33. Hold Frame

Uso de freeze frame permitido únicamente si `clip.allowFreezeFrame = true`.

---

## 34. Hold Frame Maximum

$$\text{maxFreezeExtension} = 1.50\text{ s}$$

---

## 35. Loop

Prohibidos bucles evidentes; registro obligatorio de `LOOP_USED`.

---

## 36. Alternate Take

Tomas alternativas semánticamente equivalentes superan a la repetición de una misma toma.

---

## 37. Slow Motion

La reducción de velocidad respeta siempre el límite `minPlaybackRate` del clip.

---

## 38. Compression

Compresión permitida hasta `minDuration`, nunca más allá.

---

## 39. Compression Priority

$$\text{LOW} > \text{NORMAL} > \text{HIGH} \quad (\text{CRITICAL protegido})$$

---

## 40. Extension Priority

$$\text{LOW} > \text{NORMAL} > \text{HIGH}$$

---

## 41. Critical Segment Protection

Prohibido que segmentos críticos absorban desajustes de idioma.

---

## 42. Redistribution

Transferencia de tiempo entre segmentos contiguos compatibles ($\text{segment}_i += \Delta, \; \text{segment}_j -= \Delta$).

---

## 43. Global Optimization

Minimización de error temporal, distorsión visual, alteración vocal y saltos de ancla.

---

## 44. Cost Function

$$\text{Cost} = W_{\text{voice}} \cdot \Delta_{\text{voice}} + W_{\text{visual}} \cdot \Delta_{\text{visual}} + W_{\text{repeat}} \cdot P_{\text{repeat}} + W_{\text{anchor}} \cdot \Delta_{\text{anchor}} + W_{\text{cut}} \cdot C_{\text{cut}}$$

---

## 45. No Greedy-Only Requirement

Arquitectura extensible para admitir optimizadores globales no lineales.

---

## 46. Voice Time-Stretch

Modulación de la velocidad de reproducción de la voz únicamente como recurso complementario.

---

## 47. Default Voice Stretch Range

$$[0.95\text{x}, 1.05\text{x}]$$

---

## 48. Warning Range

Valores fuera de $[0.90\text{x}, 1.10\text{x}]$ emiten advertencia formal.

---

## 49. Hard Limit

Límite infranqueable:
$$[0.85\text{x}, 1.15\text{x}]$$

---

## 50. Voice Quality Priority

$$\text{Adaptación visual} > \text{Estiramiento forzado de voz}$$

---

## 51. Voice Stretch Technology

```typescript
interface TimeStretchProvider {
  stretch(audioPath: string, rate: number): Promise<string>;
}
```

---

## 52. Time Stretch Provider

Abstracción desacoplada de la herramienta concreta de procesamiento.

---

## 53. Pitch Preservation

Conservación estricta del tono fonético natural de la voz durante el estiramiento.

---

## 54. Stretch Validation

Comprobación posterior de duración, pico dBFS, RMS y LUFS.

---

## 55. Audio Re-Alignment

Recálculo o transformación lineal de timestamps tras la aceleración/frenado de la voz.

---

## 56. Timing Transformation

$$\text{newTime} = \frac{\text{oldTime}}{\text{rate}}$$

---

## 57. Nonlinear Time Stretch

Alineación forzada obligatoria si el proveedor utiliza deformaciones no lineales.

---

## 58. B-Roll Selection

Consumo directo de candidatos evaluados por el `VlogFootageClassifier`.

---

## 59. B-Roll Candidate

```typescript
interface BrollCandidate {
  clipId: string;
  semanticScore: number;
  visualScore: number;
  duration: number;
  tags: string[];
  usableStart: number;
  usableEnd: number;
}
```

---

## 60. Semantic Compatibility

Asociación de clips mediante `semanticScore`.

---

## 61. Visual Compatibility

Filtrado por nitidez y encuadre mediante `visualScore`.

---

## 62. Candidate Ranking

$$\text{Score} = w_s \cdot \text{semantic} + w_v \cdot \text{visual} + w_d \cdot \text{durationFit} - P_{\text{repetition}}$$

---

## 63. Repetition Penalty

Penalización incremental por frescura de uso.

---

## 64. Adjacent Repetition

Prohibida la selección consecutiva del mismo clip sin autorización explícita.

---

## 65. Same-Scene Repetition

Evitar la repetición de la misma escena dentro de ventanas temporales próximas.

---

## 66. B-Roll Semantic Timing

Aparición visual sincronizada alrededor del intervalo temporal de la frase temática.

---

## 67. B-Roll Lead-In

Anticipación visual de $0.0\text{ a }0.5\text{ s}$ antes del arranque oral de la frase.

---

## 68. B-Roll Tail

Extensión de $0.0\text{ a }1.0\text{ s}$ posterior al remate de la frase.

---

## 69. Cut on Phrase Boundary

Cortes sincronizados con pausas o límites entre palabras; prohibido cortar en fonemas internos.

---

## 70. Forbidden Cut

Cero cortes visuales a mitad de una palabra pronunciada.

---

## 71. Subtitle Synchronization

Alineación de subtítulos sobre los mismos timestamps del audio localizado.

---

## 72. Subtitle Drift

$$\text{subtitleStart} \ge \text{audioStart} - \text{tolerance}, \quad \text{subtitleEnd} \le \text{audioEnd} + \text{tolerance}$$

---

## 73. Tolerance

$$\text{tolerance} = \pm 40\text{ ms}$$

---

## 74. Punch-In Compatibility

Anclaje prioritario en palabras de énfasis o cambios narrativos.

---

## 75. Punch-In Duration

Duración recomendada: $0.40\text{ a }2.00\text{ s}$.

---

## 76. Punch-In Collision

Prohibido disparar un nuevo punch-in mientras otro esté activo.

---

## 77. Transition Placement

Transiciones emplazadas en fronteras de cláusula, pausas o beats musicales.

---

## 78. Transition Duration

Límites de duración ajustados a las capacidades del preset editorial.

---

## 79. Transition Collision

Prohibida la superposición de transiciones incompatibles en la misma ventana.

---

## 80. Music Beat Alignment

Alineación secundaria a golpes de compás (BPM) subordinada a la voz.

---

## 81. Music Ducking

Generación de curvas de atenuación musical sincrónicas con la presencia de diálogo.

---

## 82. Language-Specific Pacing

```typescript
interface LanguagePacingProfile {
  language: LanguageCode;
  preferredWordsPerMinute?: number;
  minimumPhraseDuration?: number;
  maximumPhraseDensity?: number;
}
```

---

## 83. WPM

$$\text{WPM} = \frac{\text{palabras pronunciadas}}{\text{duración en minutos}}$$

---

## 84. WPM Warning

Aviso `WARNING: HIGH_SPEECH_DENSITY` ante saturación verbal.

---

## 85. WPM Is Diagnostic

El WPM es una métrica de diagnóstico; prohibido usarlo para recortar palabras arbitrariamente.

---

## 86. Language Length Adaptation

Soporte nativo para expansión ($\Delta > 0$), compresión ($\Delta < 0$) o paridad ($\Delta \approx 0$).

---

## 87. Expansion Case

Ante expansión: extensión de B-Roll, redistribución de pausas y leve estiramiento vocal.

---

## 88. Compression Case

Ante compresión: recorte de pausas redundantes y condensación de B-Roll.

---

## 89. Do Not Add Empty Space

Prohibido rellenar con planos vacíos o estáticos innecesarios ante audios más breves.

---

## 90. Do Not Cut Speech

Prohibido recortar frases orales para encajarlas en la duración visual.

---

## 91. Segment Split

División de segmentos excesivamente extensos en unidades semánticas discretas.

---

## 92. Segment Merge

Fusión de microsegmentos contiguos pertenecientes a la misma idea.

---

## 93. Minimum Visual Shot

$$\text{minVisualShot} = 0.70\text{ s}$$

---

## 94. Minimum Talking-Head Shot

$$\text{minTalkingHeadShot} = 1.00\text{ s}$$

---

## 95. Maximum Unchanged Shot

$$\text{maxUnchangedShot} = 6.00\text{ s}$$

---

## 96. Style Override

Modulación de densidades de corte y duraciones de plano mediante presets de estilo.

---

## 97. Style Priority

$$\text{Defaults} \longrightarrow \text{Style Preset} \longrightarrow \text{Project Config} \longrightarrow \text{Segment Override}$$

---

## 98. User Override

Toda instrucción manual explícita prevalece sobre cualquier heurística automática.

---

## 99. Locked Clip

```typescript
interface ClipLock {
  clipId: string;
  lockTiming: boolean;
  lockPosition: boolean;
  lockDuration: boolean;
}
```

---

## 100. Locked Timing

Con `lockDuration: true`, el clip no puede ser expandido ni comprimido automáticamente.

---

## 101. Conflict

Generación de `PACING_CONFLICT` si los locks impiden cuadrar la locución.

---

## 102. Conflict Resolution

Prohibido romper bloqueos de usuario de forma silenciosa.

---

## 103. Conflict Report

```typescript
interface PacingConflict {
  segmentId: string;
  requiredDelta: number;
  availableFlexibility: number;
  blockingConstraints: string[];
  suggestedResolution: string;
}
```

---

## 104. Hard Failure

Conflicto en evento crítico detiene la exportación (`production = BLOCKED`).

---

## 105. Soft Failure

Conflicto en segmento flexible emite advertencia y continúa.

---

## 106. Localized Timeline

```typescript
interface LocalizedTimeline {
  language: LanguageCode;
  duration: number;
  tracks: TimelineTrack[];
  anchors: TimingAnchor[];
  adaptationReport: AdaptationReport;
}
```

---

## 107. Adaptation Report

```typescript
interface AdaptationReport {
  sourceDuration: number;
  localizedVoiceDuration: number;
  finalDuration: number;
  voiceStretchRate: number;
  extendedSegments: string[];
  compressedSegments: string[];
  swappedBroll: string[];
  warnings: string[];
  conflicts: PacingConflict[];
}
```

---

## 108. Final Duration

Duración gobernada por el mayor requisito temporal entre voz y eventos críticos protegidos.

---

## 109. End Padding

Colchón temporal final: $\text{endPadding} = 0.25\text{ s}$.

---

## 110. Start Offset

Soporte de retardo inicial (`voiceStartOffset`) para cold opens e intros.

---

## 111. Cold Open

Segmentos `PRE_NARRATION` situados antes de la locución principal.

---

## 112. Intro

Intros fijas o adaptativas según configuración.

---

## 113. Outro

Outros con duración fija o adaptativa.

---

## 114. CTA

Llamadas a la acción tipificadas como `CRITICAL`.

---

## 115. Multi-Language Parallelism

Generación concurrente de timelines desacoplados (`timeline_es-MX`, `timeline_en-US`, etc.).

---

## 116. Shared Source Assets

Reutilización compartida de activos visuales, música y SFX entre variantes de idioma.

---

## 117. Language-Specific Visuals

Sustitución de gráficos o tomas específicas cuando el idioma o cultura lo demanden.

---

## 118. Graphic Text

```typescript
localizedText: Record<LanguageCode, string>;
```

---

## 119. Graphic Duration

Adaptación de la duración en pantalla según la extensión del texto traducido.

---

## 120. Text Overflow

Resolución de desbordamientos visuales mediante escalado de fuente o saltos de línea.

---

## 121. Map Labels

Mapas interactivos con toponimia localizada.

---

## 122. Geo-Badge

Uso de `displayText` en badges visuales (evitando el formateo oral del TTS).

---

## 123. Polaroid Freeze

Extensión elástica de la congelación de imagen dentro de los márgenes permitidos.

---

## 124. SFX Timing

Efectos de sonido anclados milimétricamente al evento visual detonante.

---

## 125. Camera Shutter

Disparo sincronizado de `camera_shutter.wav` al inicio del freeze-frame.

---

## 126. Transition SFX

Desplazamiento sincrónico de efectos de sonido junto con sus transiciones visuales.

---

## 127. Event Coupling

Agrupación atómica de `VisualEvent + Transition + SFX + Overlay`.

---

## 128. Atomic Event

Mover un evento desplaza automáticamente todas sus dependencias asociadas.

---

## 129. Event Graph

```typescript
interface TimelineEventGroup {
  id: string;
  events: string[];
}
```

---

## 130. No Orphan Events

Prohibida la existencia de efectos de sonido vinculados a gráficos eliminados.

---

## 131. Timeline Validation

Auditoría estricta: duraciones no negativas, ausencia de gaps accidentales y sincronía de subtítulos.

---

## 132. Overlap Policy

Clasificación de solapes: `ALLOWED`, `FORBIDDEN`, `REQUIRES_CROSSFADE`.

---

## 133. Crossfade

Respeto de límites de duración y márgenes de solape en fundidos encadenados.

---

## 134. Frame Boundary

Cuantización exacta a números enteros de fotogramas según la tasa FPS de entrega.

---

## 135. FPS

Soporte integral de tasas de fotograma arbitrarias (23.976, 24, 25, 29.97, 30, 50, 59.94, 60).

---

## 136. Time Precision

Cálculos internos continuos en segundos de punto flotante de 64 bits.

---

## 137. Floating-Point Tolerance

$$\epsilon \le 10^{-10}$$

---

## 138. Frame Quantization

$$\text{frame} = \text{round}(\text{time} \cdot \text{fps})$$

---

## 139. No One-Frame Gaps

Detección e intercepción de huecos accidentales de un fotograma ($\text{clip}_{\text{end}} + \epsilon < \text{next}_{\text{start}}$).

---

## 140. No Phantom Overlap

Detección de solapamientos espurios entre planos adyacentes.

---

## 141. Performance

Evitar el recalculo global de todo el proyecto ante cambios menores en un solo idioma.

---

## 142. Incremental Rebuild

Modificar `en-US` reconstruye únicamente `timeline_en-US` sin alterar las demás pistas.

---

## 143. Cache

Caché persistente de rankings de B-Roll y segmentaciones de frase.

---

## 144. Cache Key

$$\text{SHA-256}(\text{scriptHash} + \text{voiceoverHash} + \text{sourceTimelineHash} + \text{pacingConfigHash} + \text{language} + \text{stylePreset})$$

---

## 145. Determinism

Misma entrada y configuración genera obligatoriamente idéntico timeline editado.

---

## 146. No Randomness

Prohibida la selección estocástica sin semilla explícita.

---

## 147. Seed

Control de variación mediante `creativeSeed: number`.

---

## 148. Selection Determinism

Con idéntica semilla, idénticos candidatos producen idéntico orden y duraciones.

---

## 149. Pacing Diagnostics

Reporte de WPM, deltas de duración, cortes totales, cobertura de B-Roll y estiramiento vocal.

---

## 150. Pacing Score

$$\text{PacingScore} \in [0, 100]$$

---

## 151. Score Is Diagnostic

El score es informativo y no bloquea exportaciones salvo umbrales configurados.

---

## 152. Automatic Warning Thresholds

Alertas ante estiramientos de voz $> 1.05\text{x}$ o densidades anómalas de corte.

---

## 153. Report Example

```text
LANGUAGE: es-MX
Source duration:       08:42.000
Voice duration:        09:51.420
Delta:                +01:09.420
Voice stretch:          1.000x
B-Roll extension:       43.200 s
Segment redistribution: 26.220 s
Critical anchors moved: 0
Conflicts:              0
Warnings:               1
```

---

## 154. Test — Expansion

Prueba de adaptación de $10\text{s}$ a $12\text{s}$ sin mutilar el audio.

---

## 155. Test — Compression

Prueba de condensación de $12\text{s}$ a $10\text{s}$ sin silencios espurios.

---

## 156. Test — Critical Segment

Comprobación de que segmentos críticos retienen sus límites temporales intactos.

---

## 157. Test — Flexible Segment

Comprobación de que segmentos flexibles absorben deltas dentro de su margen.

---

## 158. Test — Locked Clip

Verificación de inmutabilidad de clips bloqueados.

---

## 159. Test — Voice Stretch

Aceptación de ajustes suaves de velocidad vocal ($1.03\text{x}$).

---

## 160. Test — Voice Stretch Hard Limit

Rechazo estricto de peticiones fuera de rango ($1.25\text{x}$).

---

## 161. Test — Pause Cut

Uso de pausas de $0.60\text{ s}$ como puntos válidos de corte de plano.

---

## 162. Test — Micro Pause

Pausas de $0.10\text{ s}$ no inducen cortes automáticos.

---

## 163. Test — Word Boundary

Cero cortes en medio de palabras habladas.

---

## 164. Test — Subtitle Alignment

Subtítulos alineados a la voz dentro de $\pm 40\text{ ms}$.

---

## 165. Test — B-Roll Semantic Match

Asignación contextualizada de tomas de comida ante menciones gastronómicas.

---

## 166. Test — B-Roll Repetition

Rechazo de asignaciones repetitivas del mismo clip en planos consecutivos.

---

## 167. Test — Multi-Language Isolation

Alterar la duración de `de-DE` no afecta la línea temporal de `en-US`.

---

## 168. Test — Determinism

Ejecuciones repetidas producen exactamente los mismos planos y anclas temporales.

---

## 169. Property-Based Test

Timelines sintéticos mantienen duraciones no negativas y cotas válidas.

---

## 170. Property — No Speech Cut

$$\text{voiceStart} \le \text{palabras requeridas} \le \text{voiceEnd}$$

---

## 171. Property — Bounds

$$\text{minDuration} \le \text{duration} \le \text{maxDuration}$$

---

## 172. Property — Event Coupling

Desplazar un evento visual traslada en paralelo sus SFX y overlays vinculados.

---

## 173. Integration Test

Prueba integral de pipeline:
$$\text{Script} \longrightarrow \text{TTS} \longrightarrow \text{VoiceoverPackage} \longrightarrow \text{Adaptive Pacing} \longrightarrow \text{Localized Timeline} \longrightarrow \text{Subtitles} \longrightarrow \text{After Effects JSX}$$

---

## 174. Regression Fixture

Fixture maestro con A-Roll, B-Roll, música, SFX, subtítulos, Geo-Badges y punch-ins en los 7 idiomas oficiales.

---

## 175. Offline Requirement

Operatividad íntegra 100% offline.

---

## 176. Failure Mode

Jerarquía ante ausencia de solución perfecta:
$$\text{Conservar voz} \longrightarrow \text{Conservar eventos críticos} \longrightarrow \text{Respetar locks} \longrightarrow \text{Minimizar daño visual} \longrightarrow \text{Emitir reporte de conflicto}$$

---

## 177. Nunca Hacer

El motor jamás deberá:
- Cortar ni omitir palabras.
- Inventar pausas inexistentes.
- Mover eventos críticos sin aviso.
- Romper clips bloqueados.
- Rellenar tiempo con B-Roll contradictorio.

---

## 178. Override Manual

Soporte para anulación manual de restricciones por segmento:

```json
{
  "segmentId": "seg_042",
  "minDuration": 4.0,
  "maxDuration": 8.0,
  "locked": false
}
```

---

## 179. Declarative DSL Compatibility

Invocación fluida desde el lenguaje declarativo:

```text
PACE {
  language = "es-MX"
  source = "master"
  voiceover = "audio_es-MX"
  strategy = "adaptive"
}
```

---

## 180. MCP Compatibility

Exposición como herramienta MCP `adapt_timeline_for_language` con validación estricta de esquema.

---

## 181. MCP Input

```typescript
interface AdaptTimelineRequest {
  projectId: string;
  sourceTimelineId: string;
  language: LanguageCode;
  voiceoverPackageId: string;
  strategy?: "CONSERVATIVE" | "BALANCED" | "AGGRESSIVE";
}
```

---

## 182. Strategy Modes

- `CONSERVATIVE`: Continuidad visual y mínima alteración.
- `BALANCED`: Equilibrio dinámico entre ritmo y cambios visuales.
- `AGGRESSIVE`: Máxima variación visual y cortes frecuentes.

---

## 183. Default Strategy

$$\text{strategy} = \text{"BALANCED"}$$

---

## 184. Output Contract

```typescript
interface AdaptTimelineResponse {
  timelineId: string;
  language: LanguageCode;
  duration: number;
  report: AdaptationReport;
  warnings: string[];
  conflicts: PacingConflict[];
}
```

---

## 185. Definition of Done

- [ ] NarrativeSegment
- [ ] Segment importance
- [ ] Timing policy
- [ ] Flexible/fixed/constrained segments
- [ ] Voice timing integration
- [ ] Phrase timing
- [ ] Pause detection
- [ ] Timing anchors
- [ ] Duration delta
- [ ] Expansion handling
- [ ] Compression handling
- [ ] B-Roll extension
- [ ] B-Roll replacement
- [ ] B-Roll repetition prevention
- [ ] Segment redistribution
- [ ] Voice time-stretch abstraction
- [ ] Pitch preservation
- [ ] Voice timing update
- [ ] Critical event protection
- [ ] Locked clip support
- [ ] Conflict detection
- [ ] Conflict report
- [ ] Subtitle synchronization
- [ ] Music beat integration
- [ ] Ducking event integration
- [ ] Punch-in integration
- [ ] Transition integration
- [ ] SFX event coupling
- [ ] Geo-Badge compatibility
- [ ] Polaroid compatibility
- [ ] Multi-language isolation
- [ ] Incremental rebuild
- [ ] Cache
- [ ] Deterministic behavior
- [ ] Diagnostic report
- [ ] Pacing score
- [ ] Property-based tests
- [ ] Integration tests
- [ ] Regression tests
- [ ] Offline tests
- [ ] MCP contract
- [ ] DSL contract

---

## 186. Estado

**Documento:** `18-VLOG-ADAPTIVE-PACING-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

---

## 187. Regla de Implementación

Este documento define exclusivamente la adaptación temporal de una edición existente a una locución localizada. No implementa directamente TTS, traducción, clasificación inicial de metraje, seguimiento facial, render JSX ni generación de mapas. Esos subsistemas se comunican mediante contratos explícitos.
