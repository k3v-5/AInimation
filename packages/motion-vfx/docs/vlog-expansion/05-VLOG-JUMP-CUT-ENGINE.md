# Vlog Jump Cut Engine & Dynamic Punch-In

**Documento:** `05-VLOG-JUMP-CUT-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog Multilingual Expansion  
**Dependencias:** `04-AUDIO-SPEECH-PIPELINE.md`, Timeline Engine, `Property<T>`, `Matrix2D`, `DynamicSpeedRampEngine`, After Effects Exporter  

---

## 1. Objetivo

Definir de manera determinista el sistema encargado de transformar el análisis de voz en una edición automática de estilo Vlog.

El módulo deberá resolver:

$$\text{SpeechAnalysis} \longrightarrow \text{Silence Candidates} \longrightarrow \text{Editorial Decisions} \longrightarrow \text{Cut Plan} \longrightarrow \text{Timeline Remap} \longrightarrow \text{Punch-In Events} \longrightarrow \text{Audio Edit Plan} \longrightarrow \text{Video Edit Plan} \longrightarrow \text{AE JSX}$$

El sistema deberá ser completamente independiente del render final.

---

## 2. Responsabilidades

`VlogJumpCutEngine` será responsable de:
- detectar silencios editables;
- decidir qué silencios eliminar;
- preservar regiones protegidas;
- generar cortes;
- recalcular tiempos;
- evitar discontinuidades inválidas;
- conservar sincronización audio/video;
- generar eventos de punch-in;
- producir un `VlogEditPlan`.

No será responsable de:
- transcribir;
- traducir;
- generar TTS;
- clasificar B-roll;
- renderizar;
- crear composiciones de After Effects.

---

## 3. Arquitectura

```
VlogJumpCutEngine
├── SilenceCandidateAnalyzer
├── SilenceDecisionEngine
├── CutPlanner
├── TimelineRemapper
├── PunchInPlanner
├── AudioBoundaryPlanner
├── EditValidator
└── VlogEditPlanSerializer
```

Cada componente deberá poder probarse independientemente.

---

## 4. Entrada principal

```typescript
interface VlogJumpCutInput {
  mediaId: string;
  duration: number;
  speechAnalysis: SpeechAnalysis;
  configuration: VlogJumpCutConfig;
}
```

---

## 5. Configuración

```typescript
interface VlogJumpCutConfig {
  silenceThreshold: number;
  minimumKeepSilence: number;
  maximumRemovalDuration: number;
  microCrossfadeDuration: number;
  preserveBreaths: boolean;
  preserveSentenceBoundaries: boolean;
  punchInEnabled: boolean;
  punchInScale: number;
  punchInDuration: number;
  punchInReturnDuration: number;
}
```

Todos los valores deberán estar centralizados. No deberán existir constantes editoriales duplicadas dentro de los algoritmos.

---

## 6. Valores iniciales

$$\text{silenceThreshold} = 0.25\text{ s}$$
$$\text{microCrossfadeDuration} = 0.010\text{ s}$$
$$\text{punchInScale} = 1.15$$

Los demás valores deberán quedar explícitamente configurables.

---

## 7. Semántica temporal

Todo intervalo utilizará:
$$[t_{\text{start}}, t_{\text{end}})$$

Por tanto:
$$\text{duration} = \text{end} - \text{start}$$

Nunca:
$$\text{duration} = \text{end} - \text{start} + 1\text{ frame}$$

---

## 8. Invariantes temporales

Todo intervalo deberá cumplir:
$$\text{start} \ge 0, \quad \text{end} > \text{start}, \quad \text{end} \le \text{sourceDuration}$$

---

## 9. Ordenamiento

Antes de cualquier análisis:
- `speechSegments`
- `words`
- `silenceRegions`
- `protectedRegions`

deberán estar ordenados por `start` ascendente.

---

## 10. Normalización

El motor deberá normalizar previamente:
- regiones solapadas;
- regiones duplicadas;
- timestamps fuera de rango;
- regiones de duración cero;
- eventos redundantes.

Los datos imposibles deberán producir error estructurado, no ser corregidos silenciosamente.

---

## 11. Silence Candidate

Un candidato tendrá:

```typescript
interface SilenceCandidate {
  id: string;
  start: number;
  end: number;
  duration: number;
  previousSpeechSegmentId?: string;
  nextSpeechSegmentId?: string;
  previousWordId?: string;
  nextWordId?: string;
  breathPresent: boolean;
  protected: boolean;
  confidence: number;
}
```

---

## 12. Generación de candidatos

Un silencio será candidato cuando:
$$\text{duration} > \text{silenceThreshold}$$
y no esté completamente dentro de una región protegida.

---

## 13. Silencios pequeños

Si:
$$\text{duration} \le \text{silenceThreshold}$$
el motor deberá conservar el silencio.

---

## 14. Silencio exactamente igual al threshold

Con $\text{threshold} = 0.25$ y $\text{duration} = 0.25$:
$$\text{Resultado} = \text{KEEP}$$

---

## 15. Silencio mayor al threshold

Con $\text{threshold} = 0.25$ y $\text{duration} = 0.50$:
será candidato a eliminación.

---

## 16. Protección de palabras

Nunca podrá generarse un corte que elimine parcialmente una palabra. Si el intervalo intersecta una palabra:
$$\text{candidate} \cap \text{word} \ne \emptyset$$
el candidato deberá ajustarse o rechazarse.

---

## 17. Protección de respiración

Si $\text{preserveBreaths} = \text{true}$ y existe una respiración protegida dentro del silencio:
$$\text{KEEP} \quad \lor \quad \text{TRIM}$$
si existen zonas claramente editables a ambos lados.

---

## 18. Sentence Boundary

Cuando $\text{preserveSentenceBoundaries} = \text{true}$, el motor deberá evitar eliminar completamente pausas que correspondan a una separación sintáctica/editorial importante.

---

## 19. Regla conservadora

Ante incertidumbre:
$$\text{KEEP}$$
La automatización no deberá priorizar agresividad sobre seguridad editorial.

---

## 20. Decision Engine

Las decisiones posibles serán:
- `KEEP`
- `REMOVE`
- `TRIM`
- `PROTECT`
- `REJECT`

---

## 21. Decision Priority

La prioridad será:
$$\text{PROTECTED} \longrightarrow \text{INVALID} \longrightarrow \text{LINGUISTIC SAFETY} \longrightarrow \text{EDITORIAL POLICY} \longrightarrow \text{REMOVE}$$

Una regla de menor prioridad nunca podrá sobreescribir una protección.

---

## 22. Maximum Removal

No se deberá permitir eliminar arbitrariamente un silencio gigantesco si la política editorial establece un máximo.

Configuración: `maximumRemovalDuration`.

Ejemplo:
- $\text{silence} = 4.0\text{ s}$
- $\text{maximumRemoval} = 2.0\text{ s}$
- $\text{Resultado} = \text{TRIM}$ (en lugar de eliminar 4 segundos).

---

## 23. TRIM

`TRIM` significa:
$$\text{eliminar únicamente una parte segura del silencio}$$
El segmento conservado deberá permanecer explícitamente registrado.

---

## 24. Cut Operation

Una operación de corte será:

```typescript
interface CutOperation {
  id: string;
  sourceStart: number;
  sourceEnd: number;
  duration: number;
  reason: string;
}
```

---

## 25. Cut Invariant

$$\text{duration} = \text{sourceEnd} - \text{sourceStart}$$

---

## 26. Cut Ordering

Los cortes deberán ordenarse por:
$$\text{sourceStart ASC}$$

---

## 27. Overlapping Cuts

Dos cortes no podrán solaparse. Si:
$$\text{cutA.end} > \text{cutB.start}$$
deberán fusionarse o producir error de planificación.

---

## 28. Adjacent Cuts

Dos cortes contiguos:
$$\text{A.end} \equiv \text{B.start}$$
podrán fusionarse.

---

## 29. Cut Plan

El resultado deberá ser:

```typescript
interface CutPlan {
  sourceDuration: number;
  cuts: CutOperation[];
  keptRanges: TimeRange[];
  outputDuration: number;
}
```

---

## 30. Output Duration

Deberá calcularse:
$$\text{outputDuration} = \text{sourceDuration} - \sum \text{cut.duration}$$

---

## 31. Floating Point

Los cálculos temporales utilizarán tolerancia definida por el Timeline Engine. No deberán realizarse comparaciones críticas utilizando igualdad binaria sin epsilon.

---

## 32. Timeline Remapping

Después de aplicar cortes:
$$\text{source time} \longrightarrow \text{output time}$$

---

## 33. Mapping Function

Conceptualmente:
```typescript
mapSourceToOutput(sourceTime: number): number | null
```

---

## 34. Source Time dentro de corte

Si $\text{sourceTime} \in [\text{cut.start}, \text{cut.end})$, el tiempo no deberá tener una representación válida en el output. La API deberá retornar `null` explícitamente.

---

## 35. Mapping posterior al corte

Si se elimina $[10, 12)$:
- $10 \longrightarrow \text{null}$
- $11 \longrightarrow \text{null}$
- $12 \longrightarrow 10$
- $13 \longrightarrow 11$

---

## 36. Mapping antes del corte

Para $t < \text{cut.start}$:
$$\text{map}(t) = t$$

---

## 37. Multiple Cuts

Con $[10, 12)$ y $[20, 23)$, los offsets acumulados deberán calcularse correctamente.

---

## 38. Timeline Remap Object

```typescript
interface TimelineRemap {
  sourceDuration: number;
  outputDuration: number;
  cuts: CutOperation[];
  mapSourceToOutput(time: number): number | null;
  mapOutputToSource(time: number): number;
}
```

---

## 39. Invertibilidad

No se requiere invertibilidad perfecta para regiones eliminadas. Sí deberá cumplirse:
$$\text{mapOutputToSource}(\text{mapSourceToOutput}(t)) \approx t$$
para cualquier tiempo válido que no pertenezca a un corte.

---

## 40. Frame Safety

El remapeo deberá ser compatible con FPS arbitrario. No se deberá asumir 30 FPS como única frecuencia.

---

## 41. Frame Quantization

La cuantización a frames deberá realizarse únicamente en la capa de export/render. El motor editorial deberá trabajar inicialmente con tiempo continuo.

---

## 42. Audio y Video

El mismo `TimelineRemap` deberá poder utilizarse para:
- video
- audio
- subtitles
- overlays
- SFX
- B-roll

Esto evita drift entre pistas.

---

## 43. Audio Cut

Los cortes de video hablado deberán corresponder a los mismos rangos de audio salvo que exista una política específica.

---

## 44. Micro-Crossfade

Después de determinar un corte:
$$\text{microCrossfadeDuration} = 10\text{ ms} \quad (0.010\text{ s})$$
será el crossfade inicial.

---

## 45. Crossfade Safety

El crossfade nunca podrá exceder el material disponible a ambos lados del corte. Si no existe material suficiente:
$$\text{crossfadeDuration} = \min(\text{configuredDuration}, \; \text{availableBefore}, \; \text{availableAfter})$$

---

## 46. Zero Crossing

Cuando sea posible, el audio deberá buscar un punto cercano de cruce por cero antes de establecer el boundary. Esto no deberá alterar significativamente el timing editorial.

---

## 47. Audio Edit

```typescript
interface AudioEdit {
  cut: CutOperation;
  fadeIn?: Fade;
  fadeOut?: Fade;
}
```

---

## 48. Video Edit

```typescript
interface VideoEdit {
  sourceRange: TimeRange;
  outputRange: TimeRange;
}
```

---

## 49. Punch-In

El `DynamicPunchIn` será una capa editorial independiente de los cortes. Objetivo:
$$100\% \longrightarrow 115\% \longrightarrow 100\%$$

---

## 50. Punch-In Trigger

Los triggers iniciales podrán ser:
- cambio de idea;
- comienzo de segmento;
- frase enfatizada;
- high-energy moment;
- transición posterior a Jump Cut.

---

## 51. Punch-In No Obligatorio

No todo Jump Cut deberá generar Punch-In. El sistema deberá tener `punchInProbability` / `policy` o una política determinista equivalente.

---

## 52. Determinismo del Punch-In

No se utilizará aleatoriedad no controlada. La misma entrada y configuración deberá generar el mismo resultado.

---

## 53. Punch-In Event

```typescript
interface PunchInEvent {
  id: string;
  start: number;
  peak: number;
  end: number;
  scaleStart: number;
  scalePeak: number;
  scaleEnd: number;
  anchor: AnchorPoint;
  reason: string;
}
```

---

## 54. Escala inicial

$$\text{scaleStart} = 1.00, \quad \text{scalePeak} = 1.15, \quad \text{scaleEnd} = 1.00$$

---

## 55. Anchor

El anchor deberá poder representar:
```typescript
interface AnchorPoint {
  x: number;
  y: number;
}
```
normalizado:
$$0 \le x \le 1, \quad 0 \le y \le 1$$

---

## 56. Face Anchor

- Si existe información facial: $\text{anchor} = \text{detectedFaceCenter}$.
- Si no existe: $\text{anchor} = \text{configuredDefaultAnchor} \; (0.5, 0.5)$.

---

## 57. Face Tracking

El motor deberá aceptar una secuencia temporal de detecciones:
```typescript
interface FaceTrackPoint {
  time: number;
  x: number;
  y: number;
  confidence: number;
}
```

---

## 58. Face Confidence

Si la confianza facial cae por debajo del threshold:
$$\text{fallback anchor}$$
No deberá producirse una cámara errática.

---

## 59. Anchor Smoothing

El movimiento del anchor deberá suavizarse para evitar jitter.

---

## 60. Deadzone

Se utilizará inicialmente la deadzone existente ($45\text{ px}$) siempre que el formato de salida sea compatible. La implementación deberá generalizarla a unidades normalizadas o relativas al frame.

---

## 61. Punch-In Motion

La escala deberá utilizar una propiedad animable existente:
```typescript
Property<number>
```
No se deberá crear un segundo sistema de interpolación.

---

## 62. Easing

La curva deberá ser configurable. Valor inicial: Bezier cubic ease-in-out.

---

## 63. Punch-In Duration

No deberá fijarse dentro del código. Configuración:
- `punchInDuration`
- `punchInPeakDuration`
- `punchInReturnDuration`

---

## 64. Punch-In Boundaries

Un punch-in no deberá cruzar un corte sin una regla explícita. Por defecto: división del evento en el corte (`split event at cut`).

---

## 65. Punch-In + Jump Cut

Si un punch-in termina exactamente en un Jump Cut:
$$\text{end} \equiv \text{cut.start}$$
se permitirá. No deberán existir eventos que accidentalmente continúen dentro de material eliminado.

---

## 66. Punch-In + B-Roll

Si posteriormente entra B-roll: el punch-in deberá terminar, salvo que una política de estilo indique lo contrario.

---

## 67. Punch-In + Aspect Ratio

El anchor deberá recalcularse según el espacio de composición. No se deberá asumir que 1920x1080 es siempre el frame final.

---

## 68. Multi-Aspect

El evento deberá poder transformarse para:
- 16:9
- 9:16
- 1:1
- 4:5
- 21:9
usando el sistema de reencuadre existente.

---

## 69. Edit Plan

El resultado completo será:

```typescript
interface VlogEditPlan {
  version: string;
  mediaId: string;
  sourceDuration: number;
  outputDuration: number;
  cuts: CutOperation[];
  timelineRemap: TimelineRemap;
  audioEdits: AudioEdit[];
  videoEdits: VideoEdit[];
  punchIns: PunchInEvent[];
  warnings: EditWarning[];
}
```

---

## 70. Warning

```typescript
interface EditWarning {
  code: string;
  message: string;
  severity: "info" | "warning";
  time?: number;
}
```

---

## 71. Error

Los errores bloqueantes deberán estar separados de warnings. Ejemplos:
- `InvalidTimeline`
- `OverlappingCuts`
- `InvalidPunchIn`
- `MissingSpeechAnalysis`
- `InvalidSourceDuration`

---

## 72. No Mutation

El engine no deberá modificar `source media` ni `SpeechAnalysis` directamente. Debe producir un nuevo `VlogEditPlan`.

---

## 73. Idempotencia

Ejecutar el análisis dos veces sobre la misma fuente no deberá duplicar cortes.

---

## 74. Re-Application Protection

El `VlogEditPlan` deberá declarar:
- `sourceMediaId`
- `sourceHash`
para evitar aplicarlo accidentalmente sobre una fuente diferente.

---

## 75. Serialization

El plan deberá poder serializarse a JSON sin perder información temporal relevante.

---

## 76. Versionado

`planVersion`, `engineVersion` y `configurationVersion` deberán formar parte del artefacto.

---

## 77. Audit Trail

Cada corte deberá poder rastrearse hasta:
$$\text{VAD region} \longrightarrow \text{silence candidate} \longrightarrow \text{decision} \longrightarrow \text{cut}$$

---

## 78. Razones de corte

Como mínimo:
- `LONG_SILENCE`
- `EXCESSIVE_PAUSE`
- `EDITORIAL_PAUSE`

---

## 79. Razones de protección

- `PROTECTED_BREATH`
- `WORD_BOUNDARY`
- `LOW_CONFIDENCE`
- `IMPORTANT_PAUSE`
- `MANUAL_PROTECTION`

---

## 80. Manual Override

Aunque el objetivo sea automatización total, el formato deberá soportar overrides:

```typescript
interface EditOverride {
  targetId: string;
  action: "KEEP" | "REMOVE" | "PROTECT";
}
```

---

## 81. Prioridad del Override

$$\text{manual override} > \text{automatic policy}$$

---

## 82. Invalid Override

Un override que apunte a un ID inexistente deberá producir `InvalidOverride` y no ser ignorado silenciosamente.

---

## 83. Test: No Silence

Entrada: speech continuo.  
Resultado: `cuts = []`, `outputDuration = sourceDuration`.

---

## 84. Test: One Silence

Entrada: speech $[0, 2)$, silence $[2, 3)$, speech $[3, 5)$, threshold $= 0.25$.  
Resultado: $\text{cut} = [2, 3)$, $\text{outputDuration} = 4.0\text{ s}$.

---

## 85. Test: Exact Threshold

Entrada: silence $[2, 2.25)$, threshold $= 0.25$.  
Resultado: `KEEP`.

---

## 86. Test: Word Protection

Si una supuesta región de silencio invade word $[2.20, 2.40)$, no podrá eliminarse ese intervalo de palabra.

---

## 87. Test: Multiple Cuts

Entrada: $[2, 3)$ y $[5, 6)$.  
Resultado: $\text{outputDuration} = \text{sourceDuration} - 2\text{ s}$ y el remapeo aplica ambos offsets.

---

## 88. Test: Adjacent Cuts

Entrada: $[2, 3)$ y $[3, 4)$.  
Resultado: $[2, 4)$ o equivalente semántico sin solapamiento.

---

## 89. Test: Overlapping Cuts

Entrada: $[2, 4)$ y $[3, 5)$.  
Resultado: $\text{merged} = [2, 5)$ si ambas decisiones son compatibles.

---

## 90. Test: Output Mapping

Con $\text{cut} = [10, 12)$:
$$\text{map}(9) = 9, \quad \text{map}(10) = \text{null}, \quad \text{map}(11) = \text{null}, \quad \text{map}(12) = 10, \quad \text{map}(13) = 11$$

---

## 91. Test: Punch-In

Entrada: punch enabled.  
Resultado: $\text{scalePeak} = 1.15$.

---

## 92. Test: Punch-In Anchor

Si el rostro está en $x = 0.63, y = 0.41$, el anchor no deberá convertirse accidentalmente en coordenadas de otro sistema.

---

## 93. Test: Low Face Confidence

Si $\text{faceConfidence} < \text{threshold}$, deberá utilizarse fallback.

---

## 94. Test: Punch-In Across Cut

Un evento que cruce $\text{cut} = [10, 12)$ deberá dividirse o rechazarse. Nunca podrá conservar una referencia inválida.

---

## 95. Test: Aspect Ratio

El mismo evento deberá poder transformarse a 1920x1080, 1080x1920, 1080x1080, 1080x1350, 2560x1080 sin producir anchors fuera de límites.

---

## 96. Property-Based Testing

Generar $N$ speech regions, $N$ silence regions, $N$ cuts, $N$ punch-ins y verificar:
- no invalid intervals
- no negative durations
- no overlapping final cuts
- no cuts inside protected words
- no output events outside timeline

---

## 97. Fuzz Testing

Se deberán probar:
- duración 0;
- duración extremadamente pequeña;
- duración extremadamente grande;
- timestamps invertidos;
- timestamps NaN;
- Infinity;
- duplicados;
- regiones superpuestas;
- listas vacías;
- confidence 0, 1, >1, <0.

---

## 98. Performance

El algoritmo de planificación deberá evitar complejidad innecesaria. Para $N$ regiones ordenadas, la detección básica deberá poder realizarse aproximadamente en $\mathcal{O}(N)$ cuando sea posible.

---

## 99. Memory

No deberá cargarse el video completo en RAM únicamente para calcular el plan editorial. El análisis deberá trabajar sobre metadata y representaciones necesarias.

---

## 100. Streaming Compatibility

La arquitectura deberá permitir posteriormente procesamiento por chunks. No deberá asumir que todo el audio debe estar simultáneamente en memoria.

---

## 101. Observabilidad

El resultado deberá permitir conocer:
- `sourceDuration`
- `removedDuration`
- `removedPercentage`
- `cutCount`
- `protectedCount`
- `punchInCount`
- `warningCount`

---

## 102. Métricas editoriales

Se podrán calcular:
- `wordsPerMinuteBefore`
- `wordsPerMinuteAfter`
- `averagePauseBefore`
- `averagePauseAfter`
para validar que el Jump Cut no haya producido un pacing absurdo.

---

## 103. Pacing Guard

El motor podrá definir límites de densidad editorial. Si la eliminación de pausas genera un ritmo fuera del rango permitido: `PacingWarning`. No deberá revertir automáticamente sin una política explícita.

---

## 104. Naturalness Guard

La eliminación masiva de silencios no deberá considerarse automáticamente mejor. El sistema deberá poder establecer:
```typescript
maximumRemovedPercentage: number
```

---

## 105. Maximum Removed Percentage

Ejemplo: $\text{maximumRemovedPercentage} = 35\%$. Si el plan supera ese valor: `PacingWarning` o bloqueo según configuración.

---

## 106. Final Validation

Antes de entregar `VlogEditPlan`:
- [ ] cuts válidos
- [ ] cuts ordenados
- [ ] cuts sin overlap
- [ ] palabras protegidas
- [ ] duración correcta
- [ ] remap válido
- [ ] audio boundaries válidos
- [ ] punch-ins válidos
- [ ] anchors válidos
- [ ] eventos dentro del output
- [ ] sourceHash presente
- [ ] version presente

---

## 107. Integración con Timeline Engine

El módulo deberá utilizar las abstracciones temporales existentes. No deberá implementar un segundo timeline engine.

---

## 108. Integración con Matrix2D

El Punch-In deberá utilizar las transformaciones existentes:
$$\text{translate} \longrightarrow \text{scale} \longrightarrow \text{translate back}$$
para escalar alrededor del anchor.

---

## 109. Transformación conceptual

Para escalar alrededor del punto $P$:
$$T(P) \cdot S(\text{scale}) \cdot T(-P)$$
La implementación deberá respetar el convenio matricial existente.

---

## 110. Integración con Property<T>

La escala deberá representarse mediante:
```typescript
Property<number>
```
permitiendo $100\% \to 115\% \to 100\%$.

---

## 111. After Effects

El `AfterEffectsExporter` recibirá el `VlogEditPlan`. El Jump Cut Engine no deberá generar JSX directamente:
$$\text{Engine} \longrightarrow \text{Plan} \longrightarrow \text{Exporter} \longrightarrow \text{JSX}$$

---

## 112. Render Independence

El plan editorial deberá poder validarse sin abrir After Effects.

---

## 113. Snapshot Tests

Se deberán crear snapshots JSON de:
- un silencio;
- múltiples silencios;
- protección;
- punch-in;
- remapping;
- combinación completa.

---

## 114. Golden Tests

Se deberán conservar casos de referencia conocidos. Cambios accidentales en el comportamiento editorial deberán producir diferencias detectables.

---

## 115. Regression Requirement

Los nuevos tests no deberán romper las 712 pruebas existentes. El objetivo de la expansión continúa siendo:
$$\text{712 / 712 PASS (100\% GREEN)}$$

---

## 116. Definition of Done

- [ ] Silence candidate analyzer implementable
- [ ] Decision engine implementable
- [ ] Cut planner implementable
- [ ] Timeline remap implementable
- [ ] Audio edit planner implementable
- [ ] Punch-in planner implementable
- [ ] Face anchor contract definido
- [ ] Fallback definido
- [ ] Multi-aspect definido
- [ ] Audit trail definido
- [ ] Override definido
- [ ] Error model definido
- [ ] Serialization definida
- [ ] Versioning definido
- [ ] Unit tests definidos
- [ ] Property tests definidos
- [ ] Fuzz tests definidos
- [ ] Performance requirements definidos
- [ ] AE integration contract definido
- [ ] Regression strategy definida

---

## 117. Estado del documento

**Documento:** `05-VLOG-JUMP-CUT-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

Este documento constituye el contrato técnico del montaje A-Roll hablado. La implementación deberá comenzar únicamente cuando las dependencias y este contrato estén aprobados.
