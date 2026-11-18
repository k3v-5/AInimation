# Vlog Jump Cut Engine & Dynamic Punch-In

**Documento:** `16-VLOG-JUMPCUT-ENGINE-DYNAMIC-PUNCH-IN.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  
**Dependencias:** Documentos 14 y 15  
**Consumidores:** Vlog Adaptive Pacing Engine, B-Roll Matcher, After Effects JSX Exporter  

---

## 1. Objetivo

Definir completamente el motor encargado de transformar A-Roll hablado bruto en una secuencia editorial limpia mediante:
- detección de silencios;
- detección de respiraciones;
- eliminación de pausas innecesarias;
- preservación de pausas narrativas;
- jump cuts;
- micro-crossfades;
- detección de palabras y fonemas;
- protección contra cortes dentro de palabras;
- detección de cambios de idea;
- generación de candidatos de punch-in;
- animación $100\% \to 115\% \to 100\%$;
- seguimiento de rostro/ojos;
- prevención de zooms excesivos;
- coordinación con B-Roll;
- validación temporal.

El motor deberá ser determinista, offline y completamente testeable.

---

## 2. Principio Fundamental

El sistema no deberá interpretar $\text{silencio} > 0.25\text{ s}$ como *eliminar siempre*. La duración del silencio será solamente una señal. La decisión deberá considerar simultáneamente:
$$\text{duración} + \text{posición} + \text{respiración} + \text{puntuación narrativa} + \text{palabras adyacentes} + \text{cambio de idea} + \text{énfasis} + \text{B-Roll disponible} + \text{ritmo global}$$

---

## 3. Pipeline

```
A-ROLL
  │
  ▼
AUDIO ANALYSIS
  │
  ├── VAD
  ├── RMS
  ├── WORD TIMESTAMPS
  ├── BREATH DETECTION
  └── SPEECH CONFIDENCE
  │
  ▼
PAUSE CLASSIFICATION
  │
  ├── REMOVE
  ├── REDUCE
  ├── KEEP
  └── REVIEW
  │
  ▼
EDIT DECISIONS
  │
  ├── JUMP CUT
  ├── B-ROLL COVERAGE
  └── PUNCH-IN
  │
  ▼
TEMPORAL VALIDATION
  │
  ▼
DECLARATIVE EDIT PLAN
```

---

## 4. Input Contract

```typescript
interface JumpCutInput {
  assetId: string;
  duration: number;
  transcript: Transcript;
  speechSegments: SpeechSegment[];
  wordTimings: WordTiming[];
  breathEvents: BreathEvent[];
  faceTracks?: FaceTrack[];
  configuration: JumpCutConfig;
}
```

---

## 5. Speech Segment

```typescript
interface SpeechSegment {
  start: number;
  end: number;
  confidence: number;
}
```

---

## 6. Word Timing

```typescript
interface WordTiming {
  word: string;
  normalizedWord: string;
  start: number;
  end: number;
  confidence: number;
}
```

---

## 7. Breath Event

```typescript
interface BreathEvent {
  start: number;
  end: number;
  confidence: number;
  intensity: number;
}
```

---

## 8. Face Track

```typescript
interface FaceTrack {
  start: number;
  end: number;
  samples: FaceSample[];
  confidence: number;
}
```

---

## 9. Face Sample

```typescript
interface FaceSample {
  timestamp: number;
  x: number;
  y: number;
  width: number;
  height: number;
  eyeCenterX?: number;
  eyeCenterY?: number;
  confidence: number;
}
```
Coordenadas normalizadas en $[0, 1]$.

---

## 10. Configuration

```typescript
interface JumpCutConfig {
  silenceRemoveThreshold: number;
  silenceKeepThreshold: number;
  minimumSpeechDuration: number;
  minimumClipDuration: number;
  crossfadeDuration: number;
  preserveBreaths: boolean;
  preserveNarrativePauses: boolean;
  maxCutFrequencyPerMinute: number;
  enablePunchIn: boolean;
  punchInScale: number;
  punchInDuration: number;
  punchOutDuration: number;
  punchInCooldown: number;
  minimumFaceConfidence: number;
  maximumPunchInPerMinute: number;
}
```

---

## 11. Default Configuration

```json
{
  "silenceRemoveThreshold": 0.25,
  "silenceKeepThreshold": 0.80,
  "minimumSpeechDuration": 0.12,
  "minimumClipDuration": 0.25,
  "crossfadeDuration": 0.010,
  "punchInScale": 1.15,
  "punchInDuration": 0.18,
  "punchOutDuration": 0.18,
  "punchInCooldown": 3.0,
  "minimumFaceConfidence": 0.80,
  "maximumPunchInPerMinute": 12
}
```

---

## 12. Silence Categories

```typescript
type PauseType =
  | "MICRO_PAUSE"
  | "BREATH"
  | "NARRATIVE"
  | "HESITATION"
  | "LONG_SILENCE"
  | "UNKNOWN";
```

---

## 13. Micro Pause

Rango: $0.05\text{ a }0.25\text{ s}$. Por defecto: `KEEP` (no eliminar automáticamente).

---

## 14. Short Silence

Rango: $0.25\text{ a }0.50\text{ s}$. Eliminable cuando no corresponda a respiración o pausa narrativa.

---

## 15. Medium Silence

Rango: $0.50\text{ a }0.80\text{ s}$. Evaluación contextualizada obligatoria.

---

## 16. Long Silence

Silencio $> 0.80\text{ s}$: candidato firme a eliminación o reducción (*trim*).

---

## 17. Breath Protection

Una respiración detectada no se elimina automáticamente. Si $\text{breathConfidence} \ge \text{threshold}$, la pausa recibe penalización contra eliminación.

---

## 18. Breath Policy

Con `preserveBreaths: true`, las pausas con respiración se preservan o reducen (`KEEP` / `REDUCE`), nunca `REMOVE` total sin override.

---

## 19. Narrative Pause Detection

Detección de pausas intencionales que preceden conclusiones, revelaciones, frases emocionales o cambios de capítulo.

---

## 20. Narrative Pause Score

```typescript
interface NarrativePauseScore {
  emotionalWeight: number;
  topicBoundary: number;
  emphasis: number;
  visualOpportunity: number;
  total: number;
}
```

---

## 21. Narrative Pause Threshold

Umbral base: $0.70$. Por encima de este valor: `KEEP`.

---

## 22. Word Boundary Rule

Prohibido realizar cortes dentro de palabras con timestamps confiables.

---

## 23. Phoneme Protection

Jerarquía de corte milimétrico:
$$\text{Límite fonético} > \text{Límite de palabra} > \text{Segmento de habla} > \text{Umbral VAD}$$

---

## 24. Boundary Safety Margin

$$\text{boundarySafetyMargin} = 0.015\text{ s} \quad (15\text{ ms})$$

---

## 25. Cut Point Optimization

Búsqueda del centro del silencio o punto de cruce por cero (*zero crossing*), evitando cortes sobre el inicio/fin del fonema.

---

## 26. Silence Removal Model

$$\text{speech } [s_1, e_1] \quad \text{--- silencio ---} \quad \text{speech } [s_2, e_2] \implies \text{speech } [s_1, e_1] \text{ micro-crossfade } \text{speech } [s_2, e_2]$$

---

## 27. Crossfade

Micro-crossfade paramétrico de $10\text{ ms}$ ($0.010\text{ s}$) en cada unión acústica.

---

## 28. Crossfade Purpose

Eliminación de clicks, pops y discontinuidades de corriente continua (DC offsets).

---

## 29. Audio Crossfade Only

El micro-crossfade aplica estrictamente a la señal de audio; el video realiza un corte neto (*hard cut*).

---

## 30. Visual Jump Cut

El video sigue el mismo recorte temporal que el audio, salvo cuando esté cubierto por B-Roll.

---

## 31. Clip Integrity

$$\text{end} > \text{start} \quad (\text{duración estrictamente positiva en todos los fragmentos})$$

---

## 32. Minimum Clip Duration

$$\text{minimumClipDuration} = 0.25\text{ s}$$

---

## 33. Adjacent Cuts

$$\text{minimumDistanceBetweenCuts} = 0.40\text{ s}$$

---

## 34. Cut Density

Monitoreo y limitación de cortes por minuto (CPM).

---

## 35. Maximum Cut Density

$$\text{maxCutFrequencyPerMinute} = 30$$
Si se supera, las eliminaciones de menor certeza se revierten.

---

## 36. Naturalness Protection

Un montaje excesivamente fragmentado se considera inválido editorialmente.

---

## 37. Sentence Protection

Prohibido eliminar pausas completas si provoca que dos oraciones pierdan cadencia natural.

---

## 38. Clause Boundary

Ponderación de fronteras oracionales (`clauseStart`, `clauseEnd`) en el algoritmo de decisión.

---

## 39. Filler Words

Detección de muletillas (`eh`, `este`, `em`, `mmm`, `like`, `you know`); no eliminarlas ciegamente sin análisis sintáctico.

---

## 40. Filler Removal

Candidato a remoción ante baja importancia semántica, pausas circundantes y ausencia de dependencia gramatical.

---

## 41. Filler Preservation

Preservación ante valor humorístico, emocional o expresivo intencional.

---

## 42. Hesitation

Transformación de vacilaciones (*"yo... eh... creo..."* $\implies$ *"yo creo..."*) únicamente bajo reglas lingüísticas seguras.

---

## 43. Reconstructed Speech

El motor recorta tiempo en pausas; jamás inventa, reordena ni altera palabras del orador.

---

## 44. Jump Cut Decision

```typescript
interface JumpCutDecision {
  start: number;
  end: number;
  action: "REMOVE" | "REDUCE" | "KEEP" | "REVIEW";
  confidence: number;
  reasons: DecisionReason[];
}
```

---

## 45. Decision Reasons

```typescript
interface DecisionReason {
  type:
    | "SILENCE_DURATION"
    | "BREATH"
    | "NARRATIVE_PAUSE"
    | "TOPIC_BOUNDARY"
    | "HESITATION"
    | "FILLER"
    | "NATURALNESS"
    | "DENSITY"
    | "BROLL_COVERAGE";
  score: number;
}
```

---

## 46. Reduce Action

Acción `REDUCE`: acortar la pausa conservando una fracción audible ($0.80\text{s} \to 0.30\text{s}$).

---

## 47. Reduction Target

$$\text{targetPauseDuration} = 0.30\text{ s}$$

---

## 48. Reduction Safety

Nunca reducir por debajo de la separación fonética mínima para evitar colisión de palabras.

---

## 49. Global Timeline Rebuild

Reconstrucción exacta de offsets del timeline tras cada corte sin acumular errores de punto flotante.

---

## 50. Time Precision

Tiempos expresados en segundos IEEE 754 de 64 bits.

---

## 51. Floating Point

Tolerancia de comparación:
$$\epsilon = 10^{-10}$$

---

## 52. Punch-In Purpose

Énfasis visual dinámico ligado a contenido narrativo, no por simple presencia de un rostro.

---

## 53. Punch-In Scale

Escalado estándar:
$$100\% \longrightarrow 115\% \longrightarrow 100\%$$

---

## 54. Maximum Scale

$$\text{maximumPunchInScale} = 1.20$$

---

## 55. Punch-In Candidates

Disparadores: `TOPIC_CHANGE`, `EMPHASIS`, `HOOK`, `CLIMAX`, `REACTION`.

---

## 56. Topic Change Trigger

Activación ante giro temático con $\text{confidence} \ge 0.75$.

---

## 57. Emphasis Trigger

Activación ante subida energética, cambio prosódico o pico RMS en palabras clave.

---

## 58. Hook Trigger

Punch-in permitido durante los primeros $3.0\text{ s}$ si la detección facial es sólida.

---

## 59. Climax Trigger

Activación en segmentos de importancia `HIGH` o `CRITICAL`.

---

## 60. Reaction Trigger

Activación ante cambios marcados de expresión facial.

---

## 61. Face Confidence

Prohibido punch-in automático con confianza facial inferior al $80\%$ ($\text{confidence} < 0.80$).

---

## 62. Eye Tracking

Uso preferente del centro de los ojos (`eyeCenter`) como punto focal de escalado.

---

## 63. Face Center Fallback

Uso del centro del rostro (`faceCenter`) si no hay seguimiento de ojos.

---

## 64. Multiple Faces

Prioridad absoluta sobre el interlocutor activo (*active speaker*).

---

## 65. Active Speaker

Determinación por correlación acústica, movimiento labial y prominencia en encuadre.

---

## 66. Ambiguous Speaker

Sin certeza suficiente, el punto focal se mantiene neutral en el centro de la pantalla.

---

## 67. Punch-In Animation

Curva Bezier suave:
$$100\% \longrightarrow 115\% \longrightarrow 100\%$$

---

## 68. Default Timing

$$0.18\text{ s entrada} \longrightarrow \text{Hold} \longrightarrow 0.18\text{ s salida}$$

---

## 69. Hold Duration

Duración del hold adaptada al evento narrativo.

---

## 70. Minimum Hold

$$\text{minimumHold} = 0.35\text{ s}$$

---

## 71. Maximum Hold

$$\text{maximumHold} = 2.50\text{ s}$$

---

## 72. Too Short Event

En eventos $< 0.50\text{ s}$, no forzar ciclos completos $100 \to 115 \to 100$ artificiales.

---

## 73. Short Punch-In

Escalado moderado ($100\% \to 112\% \to 100\%$) para eventos breves.

---

## 74. Punch-In Cooldown

Intervalo mínimo de enfriamiento:
$$\text{punchInCooldown} = 3.0\text{ s}$$

---

## 75. Punch-In Density

Máximo: $12\text{ punch-ins / minuto}$.

---

## 76. Density Backoff

Ante exceso de densidad, supresión de candidatos con menor confianza.

---

## 77. Consecutive Punch-Ins

Prohibidos ciclos rápidos consecutivos ($115 \to 100 \to 115$) sin respetar el cooldown.

---

## 78. B-Roll Priority

Si el segmento está totalmente cubierto por B-Roll:
$$\text{B-Roll} > \text{Punch-In} \implies \text{Punch-in omitido}$$

---

## 79. Partial B-Roll

En cobertura parcial de B-Roll, el punch-in se restringe a la porción descubierta de A-Roll.

---

## 80. Jump Cut vs B-Roll

Si una pausa eliminable queda cubierta por B-Roll, no se divide innecesariamente el plano base.

---

## 81. Decision Priority

$$\text{Validez temporal} > \text{Overrides manuales} > \text{B-Roll} > \text{Integridad de habla} > \text{Jump Cut} > \text{Punch-In} > \text{Polish}$$

---

## 82. Forced Override

Instrucciones manuales válidas se imponen sobre cualquier regla heurística.

---

## 83. Manual Punch-In

```typescript
interface ManualPunchIn {
  start: number;
  end: number;
  scale?: number;
  focalPoint?: Point2D;
}
```

---

## 84. Forbidden Punch-In

```typescript
interface PunchInRestriction {
  start: number;
  end: number;
  reason?: string;
}
```

---

## 85. Forbidden Example

Restricción explícita de usuario (ej. *prohibir zoom durante pausas emocionales*).

---

## 86. Camera Movement

Penalización de punch-in si el metraje original ya presenta movimientos bruscos de cámara.

---

## 87. Existing Zoom

Prohibido superponer punch-in sobre zooms ópticos preexistentes en la toma.

---

## 88. Stabilization Conflict

Cálculo de margen de recorte adicional si la toma requiere estabilización digital.

---

## 89. Crop Safety

Comprobación de que el escalado al $115\%$ no corte la cabeza o mentón del sujeto.

---

## 90. Face Edge Safety

Reducción de confianza si el rostro está excesivamente próximo al borde del frame.

---

## 91. Eye Focal Safety

El punto de los ojos debe permanecer dentro de la zona segura de encuadre.

---

## 92. Focal Point Smoothing

Suavizado temporal exponencial ($\alpha = 0.20$) compatible con `ActiveSpeakerReframing`.

---

## 93. Maximum Focal Velocity

Limitador de velocidad máxima para evitar desplazamientos erráticos del encuadre.

---

## 94. Focal Point Interpolation

Interpolación cúbica o lineal según configuración de suavizado.

---

## 95. Occlusion

Ante oclusión momentánea del rostro, mantenimiento de la última posición válida.

---

## 96. Occlusion Timeout

$$\text{occlusionTimeout} = 0.30\text{ s}$$

---

## 97. Tracking Loss

Pérdida de seguimiento $> 0.30\text{ s}$ cancela el punch-in o retorna al centro neutral.

---

## 98. Face Entry/Exit

Prohibido iniciar punch-in durante la entrada o salida inestable del sujeto en cuadro.

---

## 99. Face Stability

Exigencia de $0.20\text{ s}$ de seguimiento facial continuo y estable antes de disparar punch-in.

---

## 100. Audio-Visual Alignment

Sincronización del inicio de zoom con el comienzo fonético de la palabra de énfasis.

---

## 101. Pre-Roll

Adelanto configurable de $0.05\text{ a }0.12\text{ s}$ antes de la palabra objetivo.

---

## 102. Post-Roll

Mantenimiento temporal post-énfasis para evitar sensaciones visuales espasmódicas.

---

## 103. Emphasis Word

```typescript
interface EmphasisWord {
  wordIndex: number;
  confidence: number;
  reason: string;
}
```

---

## 104. Emphasis Detection

Evaluación conjunta de RMS acústico, tono fundamental, duración, posición y puntuación.

---

## 105. No False Emphasis

Una palabra pronunciada con mayor volumen no se clasifica automáticamente como de énfasis narrativo.

---

## 106. Editorial Importance

Mayor peso para entidades nombradas, cifras numéricas, superlativos y giros inesperados.

---

## 107. Example

*"Y costó solamente 50 pesos"* $\implies$ `50 pesos` recibe ponderación de énfasis principal.

---

## 108. Reaction Detection

Detección de desviaciones temporales respecto a la expresión facial neutral base.

---

## 109. Reaction Confidence

Exigencia de confianza superior al umbral configurado para activar punch-in por reacción.

---

## 110. Naturalness Score

```typescript
interface NaturalnessScore {
  speechContinuity: number;
  cutDensity: number;
  pausePreservation: number;
  visualContinuity: number;
  zoomDensity: number;
  total: number;
}
```

---

## 111. Naturalness Threshold

Umbral de naturalidad editorial:
$$\text{naturalnessThreshold} = 0.70$$

---

## 112. Automatic Backoff

Si la puntuación de naturalidad decae: supresión de punch-ins débiles y restitución de pausas.

---

## 113. Iterative Optimization

Pipeline en 5 pasadas: limpieza de voz $\to$ control de densidad $\to$ punch-in $\to$ auditoría de naturalidad $\to$ validación final.

---

## 114. Maximum Passes

Máximo 5 iteraciones; prohibidos bucles infinitos de optimización.

---

## 115. Idempotency

$$\text{optimize}(X) \equiv \text{optimize}(\text{optimize}(X))$$

---

## 116. Output

```typescript
interface JumpCutPlan {
  sourceAssetId: string;
  cuts: JumpCutDecision[];
  retainedSegments: RetainedSegment[];
  punchIns: PunchInPlan[];
  statistics: JumpCutStatistics;
  validation: ValidationReport;
}
```

---

## 117. Retained Segment

```typescript
interface RetainedSegment {
  sourceStart: number;
  sourceEnd: number;
  targetStart: number;
  targetEnd: number;
}
```

---

## 118. Punch-In Plan

```typescript
interface PunchInPlan {
  start: number;
  peakStart: number;
  peakEnd: number;
  end: number;
  scale: number;
  focalPoint: Point2D;
  trigger: string;
  confidence: number;
}
```

---

## 119. Statistics

```typescript
interface JumpCutStatistics {
  originalDuration: number;
  finalDuration: number;
  removedDuration: number;
  numberOfCuts: number;
  cutsPerMinute: number;
  numberOfPunchIns: number;
  punchInsPerMinute: number;
  preservedBreaths: number;
  preservedNarrativePauses: number;
  naturalnessScore: number;
}
```

---

## 120. Duration Invariant

$$\text{finalDuration} \le \text{originalDuration}$$
(El Jump Cut Engine jamás incrementa la duración del material bruto).

---

## 121. Removal Invariant

$$\text{removedDuration} \ge 0$$

---

## 122. Punch-In Invariant

El punch-in modifica la matriz de transformación espacial ($115\%$), nunca la duración del timeline.

---

## 123. Timeline Invariant

Todos los segmentos conservan progresión monótona creciente en `targetStart`.

---

## 124. Source Invariant

$$0 \le \text{sourceStart} < \text{sourceEnd} \le \text{sourceDuration}$$

---

## 125. Word Integrity Test

Ningún corte puede atravesar el intervalo $[w_{\text{start}}, w_{\text{end}}]$ de una palabra con confianza suficiente.

---

## 126. Breath Integrity Test

Con `preserveBreaths: true`, ninguna respiración con alta confianza es suprimida totalmente.

---

## 127. Crossfade Test

$$0 \le \text{crossfadeDuration} < \text{adjacentSegmentDuration}$$

---

## 128. Crossfade Default Test

Configuración predeterminada genera exactamente $0.010\text{ s}$ ($10\text{ ms}$).

---

## 129. Punch Scale Test

Generación exacta de curva de escala $1.00 \to 1.15 \to 1.00$.

---

## 130. Punch Focal Test

El punto focal coincide con el centro de los ojos dentro de la tolerancia de reframing.

---

## 131. Punch Cooldown Test

Dos eventos dentro de $3.0\text{ s}$ se unifican o el de menor prioridad se descarta.

---

## 132. Density Test

Verificación de descarte de candidatos ante superación de $12\text{ punch-ins / minuto}$.

---

## 133. Naturalness Regression Test

Prohibido degradar la puntuación de naturalidad en fixtures de prueba sin aprobación explícita.

---

## 134. Silence Fixtures

Fixtures de $0.10\text{s}$, $0.25\text{s}$, $0.30\text{s}$, $0.50\text{s}$, $0.80\text{s}$ y $1.20\text{s}$.

---

## 135. Boundary Fixtures

Casos límite: silencio en límite exacto de palabra, dentro de palabra, tras puntuación y entre oraciones.

---

## 136. Breath Fixtures

Respiración corta, respiración profunda, respiración con habla y falsos positivos acústicos.

---

## 137. Punch Fixtures

Giro temático, énfasis, hook, clímax, reacción, ausencia de rostro, rostros múltiples y pérdida de tracking.

---

## 138. Conflict Fixtures

Resolución de concurrencia entre B-Roll disponible/ausente y punch-ins manuales/automáticos.

---

## 139. Property-Based Tests

Generación aleatoria de intervalos de voz, pausas y detecciones faciales verificando invariantes.

---

## 140. Property: No Negative Time

$$\text{start} \ge 0, \quad \text{end} \ge \text{start}$$

---

## 141. Property: No Invalid Ordering

$$\text{segment}[i].\text{targetEnd} \le \text{segment}[i+1].\text{targetStart}$$

---

## 142. Property: No Word Damage

Cero cortes en intervalos fonéticos protegidos.

---

## 143. Property: Bounded Scale

$$1.00 \le \text{punchScale} \le \text{maximumPunchInScale}$$

---

## 144. Property: Deterministic Punch

Mismas entradas producen idénticos puntos focales, escalas y timestamps.

---

## 145. Property: Idempotence

Re-aplicar el plan sobre el resultado no produce modificaciones adicionales.

---

## 146. Performance Target

Procesamiento completo de $60\text{ minutos}$ de A-Roll de manera local sin red.

---

## 147. Memory Requirement

Procesamiento por ventanas temporales ante material que exceda la RAM disponible.

---

## 148. Streaming Compatibility

Procesamiento continuo por bloques de audio con fusión de fronteras.

---

## 149. Chunk Boundary

Fusión correcta de eventos de silencio divididos entre bloques contiguos.

---

## 150. Chunk Merge Test

Un silencio de $0.10\text{s}$ en chunk A y $0.20\text{s}$ en chunk B se consolida como $0.30\text{s}$.

---

## 151. Logging

Depuración estructurada de pausas, clasificaciones, decisiones, cortes y punch-ins.

---

## 152. Audit Trail

```typescript
interface DecisionAudit {
  id: string;
  inputHash: string;
  configurationHash: string;
  decision: string;
}
```

---

## 153. Configuration Hash

El hash de configuración garantiza reproducibilidad absoluta.

---

## 154. Versioning

Registro de `engineVersion`, `algorithmVersion` y `configVersion`.

---

## 155. Offline Requirement

Operación 100% offline sin servicios en la nube.

---

## 156. Provider Abstraction

Interfaces desacopladas para VAD, alineación fonética y seguimiento facial.

---

## 157. Local Provider Preference

Soporte prioritario para modelos y algoritmos locales.

---

## 158. Failure Mode

Fallo en tracking facial degrada a punch-in centrado o desactivado sin interrumpir los jump cuts.

---

## 159. Graceful Degradation

Continuidad operativa ante ausencia de analizadores secundarios opcionales.

---

## 160. Missing Word Timings

Sin timestamps por palabra, fallback conservador sobre límites de VAD con aviso.

---

## 161. Missing Breath Detection

Sin detector de respiraciones, preservación conservadora de pausas para evitar sobrecorte.

---

## 162. No Silent Failure

Toda degradación operativa emite una advertencia formal (`WARNING`).

---

## 163. Integration Contract

Entrega formal del plan declarativo `JumpCutPlan` a la siguiente etapa.

---

## 164. After Effects Handoff

El exportador traduce el plan a capas y keyframes de After Effects sin alterar las decisiones tomadas.

---

## 165. Audio Handoff

El motor de audio gestiona los micro-crossfades durante la mezcla final.

---

## 166. B-Roll Handoff

El B-Roll Matcher consulta `retainedSegments` para determinar ventanas visuales disponibles.

---

## 167. Pacing Handoff

El Adaptive Pacing Engine consume la duración depurada y los segmentos retenidos.

---

## 168. Definition of Done

- [ ] VAD integration
- [ ] Speech segmentation
- [ ] Word timing support
- [ ] Breath detection integration
- [ ] Pause classification
- [ ] Narrative pause detection
- [ ] Filler detection
- [ ] Silence removal
- [ ] Silence reduction
- [ ] Silence preservation
- [ ] Word boundary protection
- [ ] Phoneme boundary support
- [ ] 10 ms audio crossfade
- [ ] Cut density control
- [ ] Naturalness scoring
- [ ] Automatic backoff
- [ ] Topic change detection
- [ ] Emphasis detection
- [ ] Hook detection
- [ ] Climax detection
- [ ] Reaction detection
- [ ] Face tracking integration
- [ ] Eye tracking support
- [ ] Face-center fallback
- [ ] Multiple-face handling
- [ ] Focal point smoothing
- [ ] Occlusion handling
- [ ] Punch-in 100→115→100
- [ ] Punch timing
- [ ] Punch cooldown
- [ ] Punch density control
- [ ] Existing zoom detection
- [ ] Camera movement penalty
- [ ] Crop safety
- [ ] B-Roll conflict handling
- [ ] Manual overrides
- [ ] Deterministic output
- [ ] Offline operation
- [ ] Graceful degradation
- [ ] Property-based tests
- [ ] Golden tests
- [ ] Regression tests
- [ ] Performance tests
- [ ] Validation report

---

## 169. Estado

**Documento:** `16-VLOG-JUMPCUT-ENGINE-DYNAMIC-PUNCH-IN.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

---

## 170. Regla de Implementación

Este documento define exclusivamente:
$$\text{Limpieza temporal del A-Roll} + \text{Jump cuts} + \text{Protección del discurso} + \text{Punch-ins}$$

No define la generación de B-Roll, TTS, traducción, música, SFX, Geo-Badges, mapas, Polaroids ni render. Esos subsistemas consumirán este plan mediante contratos explícitos.
