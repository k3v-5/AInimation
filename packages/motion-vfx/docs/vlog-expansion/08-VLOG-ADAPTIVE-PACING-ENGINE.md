# Vlog Adaptive Pacing Engine

**Documento:** `08-VLOG-ADAPTIVE-PACING-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog Multilingual Expansion  
**Dependencias:** Timeline Engine, `MultilingualVoiceoverEngine`, `VlogJumpCutEngine`, `VlogFootageClassifier`, Audio Engine, Subtitle Engine, Reframing Engine  

---

## 1. Objetivo

Definir el sistema encargado de adaptar automáticamente el montaje audiovisual a las diferentes duraciones producidas por las distintas versiones lingüísticas de una misma narrativa.

El sistema deberá garantizar que:
$$\text{locución} + \text{B-roll} + \text{A-roll} + \text{subtítulos} + \text{SFX} + \text{música} + \text{punch-ins} + \text{overlays} + \text{transiciones}$$
permanezcan sincronizados después de cambiar de idioma.

---

## 2. Problema que resuelve

Una misma frase narrativa puede tener diferentes duraciones:
- `ES-MX` $\longrightarrow 5.20\text{ s}$
- `EN-US` $\longrightarrow 4.30\text{ s}$
- `PT-BR` $\longrightarrow 4.85\text{ s}$
- `FR-FR` $\longrightarrow 5.00\text{ s}$
- `DE-DE` $\longrightarrow 4.70\text{ s}$

El engine no deberá intentar forzar todas las versiones a la misma duración. Cada idioma deberá disponer de un timeline válido.

---

## 3. Principio fundamental

El idioma determina la duración de la voz. La duración de la voz determina la ventana narrativa. La ventana narrativa determina la adaptación visual.

$$\text{Language} \longrightarrow \text{Voiceover duration} \longrightarrow \text{Narrative segment duration} \longrightarrow \text{Visual adaptation} \longrightarrow \text{Final timeline}$$

---

## 4. Responsabilidad del módulo

El módulo será responsable de:
- calcular diferencias temporales;
- adaptar clips;
- extender o recortar B-roll;
- seleccionar material alternativo;
- ajustar velocidad dentro de límites;
- aplicar time-stretch de voz únicamente cuando corresponda;
- preservar puntos narrativos;
- desplazar eventos posteriores;
- mantener sincronización global.

---

## 5. Fuera del alcance

Este módulo NO será responsable de:
- traducir texto;
- generar voz;
- clasificar A-roll/B-roll;
- detectar rostros;
- generar mapas;
- generar SFX;
- generar subtítulos desde cero.

---

## 6. Input principal

```typescript
interface AdaptivePacingRequest {
  projectId: string;
  sourceTimeline: Timeline;
  sourceLanguage: SupportedLanguage;
  targetLanguage: SupportedLanguage;
  voiceover: VoiceoverManifest;
  narrativeMap: NarrativeMap;
  pacingConfig: AdaptivePacingConfig;
}
```

---

## 7. Narrative Segment

La unidad fundamental de adaptación será el segmento narrativo:

```typescript
interface NarrativeSegment {
  id: string;
  sourceStart: number;
  sourceEnd: number;
  sourceDuration: number;
  text: string;
  category: NarrativeCategory;
}
```

---

## 8. Narrative Categories

```typescript
type NarrativeCategory =
  | "HOOK"
  | "INTRO"
  | "EXPOSITION"
  | "ACTION"
  | "TRANSITION"
  | "CLIMAX"
  | "REFLECTION"
  | "CTA"
  | "OUTRO";
```

---

## 9. Shared Narrative IDs

Cada versión lingüística deberá utilizar los mismos IDs: `N001`, `N002`, `N003`, `N004`, etc.

Ejemplo:
- `N001` = Hook
- `N002` = llegada a Guadalajara
- `N003` = visita al restaurante
- `N004` = conclusión

---

## 10. Voiceover Mapping

```typescript
interface LocalizedNarrativeSegment {
  narrativeId: string;
  language: SupportedLanguage;
  audioStart: number;
  audioEnd: number;
  duration: number;
}
```

---

## 11. Target Duration

Para cada segmento:
$$\text{targetDuration} = \text{localizedVoiceover.end} - \text{localizedVoiceover.start}$$

---

## 12. Duration Delta

$$\text{delta} = \text{targetDuration} - \text{sourceDuration}$$

Interpretación:
- $\text{delta} > 0$: requiere expansión.
- $\text{delta} < 0$: requiere compresión.

---

## 13. Tolerancia

No deberá realizarse adaptación por diferencias insignificantes:
```typescript
durationTolerance: number; // Valor inicial: 0.08 s
```
Si $|\text{delta}| \le 0.08\text{ s}$, se considerará suficientemente sincronizado.

---

## 14. Adaptation Strategy

```typescript
type PacingStrategy =
  | "NONE"
  | "TRIM"
  | "EXTEND"
  | "RIPPLE"
  | "SPEED"
  | "VOICE_STRETCH"
  | "ALTERNATE_BROLL"
  | "COMPOSITE";
```

---

## 15. Strategy Priority

La prioridad inicial será:
1. `NONE`
2. `TRIM`
3. `EXTEND`
4. `ALTERNATE_BROLL`
5. `RIPPLE`
6. `SPEED`
7. `VOICE_STRETCH`
8. `COMPOSITE`

---

## 16. Regla General

La adaptación visual deberá preferirse sobre modificar artificialmente la voz:
$$\text{visual adaptation} > \text{voice time-stretch}$$

---

## 17. Voice Stretch

El time-stretch de voz únicamente podrá utilizarse dentro del rango:
$$0.95\text{x} \le \text{stretch} \le 1.05\text{x}$$

---

## 18. Voice Stretch Factor

```typescript
interface VoiceStretchConfig {
  enabled: boolean;
  minRate: 0.95;
  maxRate: 1.05;
}
```

---

## 19. Cálculo de Stretch

Si la voz debe durar $5.00\text{ s}$ y actualmente dura $5.20\text{ s}$, el engine podrá aplicar una velocidad aproximada:
$$\frac{5.20}{5.00} = 1.04\text{x}$$
siempre que esté dentro del límite.

---

## 20. Nunca Exceder Límites

Si se requiere $1.12\text{x}$, no deberá aplicarse; se deberá cambiar a estrategia visual.

---

## 21. Visual Adaptation

La adaptación visual podrá modificar:
- duración del B-roll;
- número de clips;
- puntos de corte;
- velocidad;
- hold frames;
- repetición controlada;
- selección de B-roll alternativo.

---

## 22. A-Roll Policy

El A-roll hablado no deberá recortarse dentro de una palabra. Los límites deberán respetar timestamps de palabra.

---

## 23. A-Roll Speech Safety

Nunca se deberá producir:
$$\text{word\_start} < \text{clip\_end} < \text{word\_end}$$
salvo que exista una política explícita de audio overlap.

---

## 24. B-Roll Flexibility

El B-roll tendrá mayor libertad temporal que el A-roll. Podrá: `trim`, `extend`, `speed`, `replace`, `repeat` según configuración.

---

## 25. B-Roll Extension

Si falta duración ($\text{delta} > 0$), se intentará primero extender un clip compatible.

---

## 26. Hold Frame

Un B-roll podrá finalizar mediante freeze frame si `holdFrameEnabled = true` y la extensión requerida está dentro de $\text{maxHoldDuration} = 1.50\text{ s}$.

---

## 27. B-Roll Loop

El loop deberá estar deshabilitado por defecto para metraje natural. Si se habilita: $\text{maxLoopCount} = 1$. No se deberá repetir indefinidamente una toma.

---

## 28. B-Roll Alternate

Si un segmento tiene varias tomas compatibles (`BROLL_01`, `BROLL_02`, `BROLL_03`), el engine podrá seleccionar otra toma para absorber diferencias temporales.

---

## 29. Alternate Selection Score

La selección deberá considerar:
- `semanticScore`
- `visualQuality`
- `durationFit`
- `continuityScore`
- `alreadyUsedPenalty`

---

## 30. Semantic Compatibility

Un B-roll sobre restaurante no deberá sustituirse automáticamente por uno de aeropuerto aunque tenga una duración perfecta.

---

## 31. Visual Continuity

El engine deberá evitar saltos incompatibles de orientación, posición, escala, sujeto, iluminación o dirección de movimiento.

---

## 32. Trim Policy

Cuando un clip pueda recortarse:
$$\text{trim} > \text{alternate}$$
si el recorte no elimina un evento visual importante.

---

## 33. Protected Regions

Los clips podrán contener regiones protegidas:

```typescript
interface ProtectedRegion {
  start: number;
  end: number;
  reason:
    | "SUBJECT_ACTION"
    | "FACIAL_REACTION"
    | "OBJECT_ENTRY"
    | "OBJECT_EXIT"
    | "TRANSITION"
    | "CUSTOM";
}
```

---

## 34. Trim Safety

Nunca deberá cortarse una región protegida salvo override explícito.

---

## 35. Visual Event Markers

El footage podrá declarar:

```typescript
interface VisualEvent {
  time: number;
  type: string;
  importance: number; // 0.0 a 1.0
}
```

---

## 36. Importance

- $0.0 \longrightarrow$ irrelevante
- $1.0 \longrightarrow$ crítico

Los eventos con importancia alta deberán conservarse.

---

## 37. Speed Adaptation

La velocidad visual podrá modificarse cuando el material lo permita. Configuración inicial:
$$0.85\text{x} \le \text{visualSpeed} \le 1.15\text{x}$$

---

## 38. No Extreme Speed

El engine no deberá convertir automáticamente un plano normal en $0.40\text{x}$ o $2.50\text{x}$ para resolver un problema de sincronización.

---

## 39. Action Footage

Para timelapses o acción: $0.50\text{x} \le \text{speed} \le 2.00\text{x}$ podrá ser permitido mediante capability específica del clip.

---

## 40. Clip Capabilities

```typescript
interface ClipTimingCapabilities {
  canTrim: boolean;
  canExtend: boolean;
  canFreeze: boolean;
  canLoop: boolean;
  canSpeedChange: boolean;
  minSpeed: number;
  maxSpeed: number;
}
```

---

## 41. Timeline Ripple

Cuando un segmento cambia de duración:
$$\text{segment duration changes} \longrightarrow \text{subsequent events shift}$$
La operación deberá ser un ripple edit determinista.

---

## 42. Anchored Events

Algunos eventos deberán permanecer anclados:
- `projectStart`
- `chapterStart`
- `CTA`
- `music cue`
- `specific SFX`

---

## 43. Anchor Policy

```typescript
type AnchorPolicy =
  | "RIPPLE"
  | "LOCK_TO_NARRATIVE"
  | "LOCK_TO_ABSOLUTE_TIME";
```

---

## 44. Default Anchor

- Eventos narrativos: `LOCK_TO_NARRATIVE`.
- Eventos puramente temporales: `RIPPLE`.

---

## 45. Absolute Events

Un evento marcado `LOCK_TO_ABSOLUTE_TIME` no deberá desplazarse sin producir un warning/error según configuración.

---

## 46. Music

La música deberá seguir el timeline final. No deberá utilizarse la duración original como referencia después de la adaptación.

---

## 47. Music Loop

Si la música necesita extensión, el loop o cambio de música deberá utilizar el Audio Engine existente.

---

## 48. SFX

Los SFX deberán estar asociados a eventos narrativos cuando sea posible (ej. `N003` $\to$ `camera_shutter`). El SFX se desplazará con `N003`.

---

## 49. SFX Absolute Timing

Un SFX podrá permanecer absoluto únicamente si se marca explícitamente.

---

## 50. Subtitle Synchronization

Los subtítulos deberán reconstruirse o remapearse a partir del alignment del idioma objetivo. No se deberán reutilizar timestamps del idioma fuente.

---

## 51. Subtitle Rule

$$\text{localized voice timestamps} \longrightarrow \text{localized subtitle timestamps}$$

---

## 52. Karaoke

El karaoke palabra por palabra deberá utilizar `AlignmentWord[]` del idioma objetivo.

---

## 53. Punch-In Synchronization

Los punch-ins deberán estar vinculados a eventos narrativos o palabras. El cambio de idioma no deberá destruir esta asociación.

---

## 54. Punch-In Mapping

```typescript
interface NarrativeVisualEvent {
  narrativeId: string;
  relativeTime: number;
  type: "PUNCH_IN" | "PUNCH_OUT" | "CUT" | "OVERLAY";
}
```

---

## 55. Relative Timing

Los eventos narrativos deberán almacenarse preferentemente como `relativeTime` dentro del segmento, permitiendo que el segmento cambie de duración.

---

## 56. Relative Time Scaling

Si un segmento cambia de $5\text{s}$ a $6\text{s}$, un evento situado a los $2.5\text{s}$ podrá trasladarse proporcionalmente a:
$$\frac{2.5}{5} \times 6 = 3.0\text{ s}$$
cuando el evento sea escalable.

---

## 57. Non-Scalable Events

Los eventos críticos podrán utilizar posición semántica (`BEFORE_WORD`, `AT_WORD`, `AFTER_WORD`) en lugar de proporción temporal.

---

## 58. Event Priority

$$\text{word anchor} > \text{semantic anchor} > \text{relative time} > \text{absolute time}$$

---

## 59. Transition Adaptation

Una transición no deberá cruzar una palabra hablada crítica.

---

## 60. Transition Duration

Si una transición causa conflicto, se reducirá la transición antes de modificar la voz.

---

## 61. Minimum Transition Duration

$$\text{minimumTransitionDuration} = 0.08\text{ s}$$

---

## 62. Crossfade Audio

Los cambios de audio deberán conservar micro-crossfades para evitar clicks.

---

## 63. Segment Boundary

Cada segmento deberá terminar en una frontera editorial válida:
$$\text{sentence end} > \text{clause end} > \text{breath} > \text{word boundary}$$

---

## 64. Breath Alignment

Si existe información respiratoria ($\text{breath} > 0.30\text{s}$), podrá utilizarse como candidato de corte.

---

## 65. Hook Protection

Los primeros $3\text{ segundos}$ del vídeo tendrán protección adicional (`hookProtection: { enabled: true, duration: 3 }`). No deberá ralentizarse innecesariamente el Hook.

---

## 66. Pacing Score

```typescript
interface PacingScore {
  averageShotDuration: number;
  cutsPerMinute: number;
  speechDensity: number;
  visualChangeRate: number;
  score: number;
}
```

---

## 67. Pacing Stability

La localización no deberá producir accidentalmente saltos extremos ($1\text{s} \to 14\text{s} \to 0.5\text{s}$) como consecuencia de una sola traducción.

---

## 68. Maximum Segment Expansion

$$\text{maxSegmentExpansionRatio} = 1.50$$
Si un segmento supera este límite, deberá evaluarse una estructura alternativa.

---

## 69. Maximum Segment Compression

$$\text{maxSegmentCompressionRatio} = 0.60$$
No se deberá comprimir un segmento por debajo de este ratio sin override.

---

## 70. Structural Reflow

Si un segmento no puede adaptarse localmente:
$$\text{local adaptation} \longrightarrow \text{neighbor adaptation} \longrightarrow \text{structural reflow}$$

---

## 71. Neighbor Adaptation

El engine podrá tomar o devolver tiempo de segmentos visuales flexibles adyacentes. Nunca deberá mover una frase a otra narrativa sin actualizar el `NarrativeMap`.

---

## 72. Fixed Content

Algunos clips podrán declararse `fixedDuration: true`; estos no podrán modificarse.

---

## 73. Fixed Visual Event

Un momento cinematográfico importante podrá declararse `LOCKED` y el engine deberá adaptar el material alrededor de él.

---

## 74. Timeline Conflict

Si no existe solución válida:
$$\text{AdaptivePacingConflictError}$$
No se deberá producir un vídeo aparentemente correcto pero desincronizado.

---

## 75. Conflict Report

```typescript
interface PacingConflict {
  narrativeId: string;
  requiredDuration: number;
  availableDuration: number;
  constraints: string[];
  attemptedStrategies: PacingStrategy[];
}
```

---

## 76. Dry Run

Antes de modificar el timeline final deberá existir:
```typescript
plan(request: AdaptivePacingRequest): PacingPlan
```

---

## 77. Pacing Plan

```typescript
interface PacingPlan {
  sourceDuration: number;
  targetDuration: number;
  operations: PacingOperation[];
  warnings: PacingWarning[];
}
```

---

## 78. Pacing Operation

```typescript
interface PacingOperation {
  id: string;
  narrativeId: string;
  strategy: PacingStrategy;
  amount: number;
  reason: string;
}
```

---

## 79. Plan Validation

El plan deberá validarse antes de aplicarse:
$$\text{plan} \longrightarrow \text{validate} \longrightarrow \text{apply} \longrightarrow \text{validate final timeline}$$

---

## 80. Atomic Timeline Mutation

Si `apply()` falla, el timeline original deberá permanecer intacto.

---

## 81. Transaction Model

$$\text{BEGIN} \longrightarrow \text{clone timeline} \longrightarrow \text{apply operations} \longrightarrow \text{validate} \longrightarrow \text{COMMIT (o ROLLBACK)}$$

---

## 82. Deterministic Ordering

Las operaciones deberán ejecutarse en orden estable:
$$\text{narrative order} \longrightarrow \text{operation priority} \longrightarrow \text{operation ID}$$

---

## 83. Multi-Language Batch

Podrá procesarse `ES-MX`, `EN-US`, `PT-BR`, `FR-FR`, `DE-DE` en una misma ejecución.

---

## 84. Source Timeline Immutability

El timeline original nunca deberá modificarse. Cada idioma recibirá una copia independiente.

---

## 85. Output

```typescript
interface AdaptiveTimelineResult {
  language: SupportedLanguage;
  timeline: Timeline;
  duration: number;
  pacingScore: PacingScore;
  operations: PacingOperation[];
  warnings: PacingWarning[];
}
```

---

## 86. Validation — Audio

El timeline final deberá tener: voz que inicia/termina correctamente, sin gaps accidentales ni solapamientos destructivos.

---

## 87. Validation — Video

No negative durations, no invalid source ranges, no overlapping exclusive clips, no orphan layers.

---

## 88. Validation — Subtitles

$$\text{subtitle.start} \ge \text{voice.start}, \quad \text{subtitle.end} \le \text{voice.end}$$
salvo tolerancia configurable.

---

## 89. Validation — SFX

Los eventos SFX deberán referenciar un evento válido.

---

## 90. Validation — Transitions

$$\text{transition.duration} \le \text{available neighboring media}$$

---

## 91. Validation — Aspect Ratio

La adaptación temporal no deberá romper las proporciones 16:9, 9:16, 1:1, 4:5, 21:9.

---

## 92. Validation — Safe Zones

Los overlays deberán conservar sus constraints aunque cambie la duración.

---

## 93. Performance

El planner deberá operar sobre metadata siempre que sea posible, sin renderizar vídeo.

---

## 94. Render Independence

La planificación temporal deberá poder probarse sin After Effects.

---

## 95. After Effects

After Effects recibirá el timeline final ya resuelto; no contendrá lógica de decisión de pacing.

---

## 96. JSX Contract

El exportador JSX recibirá el timeline resuelto junto con los assets, subtítulos y audios localizados.

---

## 97. No Hidden Logic in JSX

El JSX no deberá decidir qué B-roll, duración, idioma o stretch aplicar.

---

## 98. Test — Longer Spanish

Fuente: $5.0\text{ s}$, ES: $6.0\text{ s}$.  
Esperado: extensión visual sin stretch superior a $1.05\text{x}$.

---

## 99. Test — Shorter English

Fuente: $5.0\text{ s}$, EN: $4.2\text{ s}$.  
Esperado: visual trim / alternate B-roll antes de aplicar stretch extremo.

---

## 100. Test — Small Difference

Fuente: $5.00\text{ s}$, Destino: $5.05\text{ s}$.  
Esperado: `NONE` debido a la tolerancia ($0.08\text{ s}$).

---

## 101. Test — Extreme Difference

Fuente: $5.0\text{ s}$, Destino: $8.0\text{ s}$.  
Esperado: no extreme voice stretch y generación de plan visual/estructural.

---

## 102. Test — Protected Region

Un clip con `protected = 2.0–3.0s` no deberá recortarse dentro de esa región.

---

## 103. Test — Word Boundary

Un A-roll no deberá terminar en mitad de una palabra.

---

## 104. Test — Narrative Event

Un punch-in asociado a `N003` con `relativeTime = 2.0` deberá continuar asociado a `N003` después de la adaptación.

---

## 105. Test — Ripple

Si `N002` gana $+1.0\text{s}$, los segmentos posteriores deberán desplazarse $+1.0\text{s}$ salvo eventos bloqueados.

---

## 106. Test — Locked Event

Un evento `LOCK_TO_ABSOLUTE_TIME` deberá permanecer en su posición o producir conflicto.

---

## 107. Test — Alternate B-Roll

Si el B-roll actual no puede absorber la duración y existe una alternativa compatible, `ALTERNATE_BROLL` deberá evaluarse antes de forzar speed extrema.

---

## 108. Test — No Compatible B-Roll

Si no existe material compatible: `PacingWarning` o `AdaptivePacingConflictError` según severidad.

---

## 109. Test — Multi-Language Isolation

Modificar EN no deberá modificar los timelines de ES, PT, FR o DE.

---

## 110. Test — Idempotency

Aplicar el mismo `PacingPlan` dos veces no deberá duplicar operaciones.

---

## 111. Property-Based Testing

Generar timelines aleatorios y comprobar:
$$\text{no negative durations}, \quad \text{no invalid source ranges}, \quad \text{no broken narrative references}$$

---

## 112. Property — Timeline Conservation

Todo contenido no marcado como eliminable deberá conservarse.

---

## 113. Property — Narrative Conservation

Los IDs narrativos no deberán perderse durante la adaptación.

---

## 114. Property — Ordering

Si $N_{001} < N_{002} < N_{003}$, el timeline final deberá conservar $N_{001} < N_{002} < N_{003}$.

---

## 115. Property — Audio Sync

Para cada segmento:
$$\text{voiceover duration} \equiv \text{resolved narrative duration} \pm \epsilon$$

---

## 116. Property — No Extreme Stretch

Nunca $\text{stretch} < 0.95$ ni $\text{stretch} > 1.05$ salvo configuración explícita de override.

---

## 117. Regression Suite

Cada bug histórico deberá convertirse en una prueba permanente (`pacing-regression-XXXX`).

---

## 118. Golden Timeline

Deberán existir timelines de referencia: `golden_es.json`, `golden_en.json`, `golden_pt.json`, `golden_fr.json`, `golden_de.json`.

---

## 119. Golden Comparison

El test deberá comparar orden de eventos, duraciones, asset IDs, IDs narrativos y referencias de audio/subtítulos.

---

## 120. Logging

Cada adaptación registrará: `sourceDuration`, `targetDuration`, `delta`, `strategy`, `asset`, `oldDuration`, `newDuration`, `stretch`, `reason`.

---

## 121. Explainability

El engine deberá poder responder estructuradamente por qué cada clip cambió de duración.

---

## 122. Debug Artifact

Cada ejecución podrá producir `pacing-plan.json` para auditoría.

---

## 123. Configuration

```typescript
interface AdaptivePacingConfig {
  durationTolerance: number;
  voiceStretch: VoiceStretchConfig;
  visualSpeed: {
    enabled: boolean;
    min: number;
    max: number;
  };
  freezeFrame: {
    enabled: boolean;
    maxDuration: number;
  };
  looping: {
    enabled: boolean;
    maxLoopCount: number;
  };
  alternateBroll: {
    enabled: boolean;
  };
  structuralReflow: {
    enabled: boolean;
  };
  hookProtection: {
    enabled: boolean;
    duration: number;
  };
}
```

---

## 124. Default Configuration

```json
{
  "durationTolerance": 0.08,
  "voiceStretch": {
    "enabled": true,
    "minRate": 0.95,
    "maxRate": 1.05
  },
  "visualSpeed": {
    "enabled": true,
    "min": 0.85,
    "max": 1.15
  },
  "freezeFrame": {
    "enabled": true,
    "maxDuration": 1.5
  },
  "looping": {
    "enabled": false,
    "maxLoopCount": 1
  },
  "alternateBroll": {
    "enabled": true
  },
  "structuralReflow": {
    "enabled": true
  },
  "hookProtection": {
    "enabled": true,
    "duration": 3
  }
}
```

---

## 125. Definition of Done

- [ ] Narrative IDs definidos
- [ ] Localized timing definido
- [ ] Duration delta definido
- [ ] Tolerance definida
- [ ] Strategy hierarchy definida
- [ ] Voice stretch limitado
- [ ] A-roll protection definida
- [ ] B-roll adaptation definida
- [ ] Alternate B-roll definido
- [ ] Freeze frame definido
- [ ] Loop policy definida
- [ ] Visual speed definida
- [ ] Protected regions definidas
- [ ] Visual events definidos
- [ ] Relative timing definido
- [ ] Punch-in mapping definido
- [ ] Transition handling definido
- [ ] Audio handling definido
- [ ] Subtitle synchronization definido
- [ ] SFX synchronization definido
- [ ] Music synchronization definido
- [ ] Ripple definido
- [ ] Anchors definidos
- [ ] Conflict handling definido
- [ ] Dry-run planner definido
- [ ] Transaction/rollback definido
- [ ] Multi-language isolation definido
- [ ] After Effects contract definido
- [ ] Unit tests definidos
- [ ] Property tests definidos
- [ ] Golden tests definidos
- [ ] Regression tests definidos
- [ ] Explainability definida
- [ ] Debug artifacts definidos

---

## 126. Estado del documento

**Documento:** `08-VLOG-ADAPTIVE-PACING-ENGINE.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

Este documento establece que la localización lingüística no debe "forzar" el vídeo a una duración arbitraria. El sistema debe construir un plan de adaptación verificable, aplicar las modificaciones dentro de límites explícitos y fallar de manera visible cuando las restricciones hagan imposible obtener un timeline válido.
