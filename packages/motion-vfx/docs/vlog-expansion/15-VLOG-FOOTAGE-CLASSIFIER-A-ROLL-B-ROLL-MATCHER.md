# Vlog Footage Classifier & A-Roll / B-Roll Matcher

**Documento:** `15-VLOG-FOOTAGE-CLASSIFIER-A-ROLL-B-ROLL-MATCHER.md`  
**Versión:** `1.0.0`  
**Estado:** DRAFT TÉCNICO  
**Sistema:** Motor Audiovisual v3.4.0 + Vlog & Multilingual Expansion  
**Dependencias:** Documento 14 — Vlog Ingestion & Media Analysis Engine  
**Consumidores:** Vlog Jump Cut Engine, Dynamic Punch-In, Adaptive Pacing Engine, After Effects JSX Exporter  

---

## 1. Objetivo

Definir completamente el sistema responsable de:
- clasificar material audiovisual;
- separar A-Roll y B-Roll;
- detectar Action y Timelapse;
- determinar la calidad editorial de cada toma;
- extraer intención visual;
- relacionar contenido hablado con material visual;
- seleccionar candidatos B-Roll;
- evitar repeticiones;
- evitar asociaciones visuales incorrectas;
- calcular scores de compatibilidad;
- resolver conflictos;
- respetar restricciones temporales;
- producir un plan editorial determinista.

El resultado deberá ser una estructura que indique: qué clip usar, cuándo usarlo, durante cuánto tiempo, sobre qué frase, con qué prioridad, con qué confianza y por qué fue seleccionado.

---

## 2. Principio Editorial

El sistema no deberá interpretar *"hay una toma de un restaurante"* como suficiente para insertar *"restaurante"* en cualquier momento. La selección deberá considerar simultáneamente:
$$\text{semántica} + \text{temporalidad} + \text{calidad} + \text{continuidad} + \text{contexto narrativo} + \text{composición} + \text{duración} + \text{repetición} + \text{relevancia}$$

---

## 3. Pipeline

```
INGESTION MANIFEST
        │
        ▼
FEATURE NORMALIZATION
        │
        ▼
ASSET CLASSIFICATION
        │
        ├──────────────┐
        ▼              ▼
     A-ROLL         B-ROLL
        │              │
        │       SEMANTIC INDEX
        │              │
        └──────┬───────┘
               ▼
        TRANSCRIPT INPUT
               │
               ▼
       SEMANTIC SEGMENTS
               │
               ▼
       CANDIDATE GENERATION
               │
               ▼
       COMPATIBILITY SCORING
               │
               ▼
       CONFLICT RESOLUTION
               │
               ▼
       EDITORIAL PLAN
```

---

## 4. Classification Types

```typescript
type FootageType =
  | "A_ROLL"
  | "B_ROLL"
  | "ACTION"
  | "TIMELAPSE"
  | "SCREEN"
  | "PHOTO"
  | "OTHER";
```

---

## 5. Classification Is Probabilistic

El sistema deberá producir distribuciones de probabilidad normalizadas en $[0.0, 1.0]$:

```typescript
interface ClassificationScores {
  aRoll: number;
  bRoll: number;
  action: number;
  timelapse: number;
  screen: number;
  other: number;
}
```

---

## 6. Final Classification

```typescript
interface FootageClassification {
  primaryType: FootageType;
  scores: ClassificationScores;
  confidence: number;
  reasons: ClassificationReason[];
}
```

---

## 7. Classification Reasons

```typescript
interface ClassificationReason {
  feature: string;
  contribution: number;
  explanation: string;
}
```

Ejemplo:
```json
{
  "feature": "speech",
  "contribution": 0.82,
  "explanation": "Continuous speech detected with face visible."
}
```

---

## 8. A-Roll Definition

A-Roll será material cuya función principal sea transportar narración, diálogo, presentación, entrevista o explicación.

---

## 9. A-Roll Indicators

Indicadores positivos: habla continua, presencia de rostro, mirada directa a cámara, encuadre estable, voz limpia y planos medios/cortos.

---

## 10. A-Roll Score

Ponderación inicial (configurable):
- Speech: $35\%$
- Face: $20\%$
- Camera-facing: $15\%$
- Audio quality: $10\%$
- Framing: $10\%$
- Stability: $5\%$
- Quality: $5\%$

---

## 11. B-Roll Definition

B-Roll será material utilizado como soporte visual de una narración o transición (calles, comida, paisajes, hoteles, monumentos, actividades, detalles).

---

## 12. B-Roll Indicators

Indicadores positivos: prominencia visual, riqueza semántica, bajo diálogo directo a cámara, composición útil y movimiento cinemático estable o intencional.

---

## 13. B-Roll Does Not Mean "No Speech"

Un clip con voz de fondo o incidental puede seguir siendo B-Roll (ej. persona caminando mientras conversa fuera de cámara: $\text{B\_ROLL} = 0.72, \; \text{A\_ROLL} = 0.38$).

---

## 14. Action Classification

Deportes, carreras, conducción, movimientos rápidos, atracciones, actividad física y desplazamientos bruscos intencionales de cámara.

---

## 15. Timelapse Classification

Progresión temporal acelerada e iluminación de frecuencia anormal; independiente de clips a alta tasa de cuadros (*high FPS*).

---

## 16. Screen Classification

Capturas de pantalla de interfaces de escritorio, aplicaciones móviles, sitios web o sesiones de software.

---

## 17. Photo Classification

Fotografías e imágenes estáticas con duración configurable y movimiento nulo ($\text{motion} = 0$).

---

## 18. Semantic Feature Extraction

```typescript
interface VisualSemantics {
  tags: SemanticTag[];
  objects: DetectedObject[];
  locations: LocationCandidate[];
  activities: ActivityCandidate[];
  environments: EnvironmentCandidate[];
}
```

---

## 19. Semantic Tag

```typescript
interface SemanticTag {
  value: string;
  confidence: number;
  source: string;
}
```

---

## 20. Object Detection

Objetos reconocibles: `person`, `car`, `bus`, `building`, `food`, `drink`, `phone`, `camera`, `laptop`, `street`, `sign`, `tree`, `mountain`, `ocean`.

---

## 21. Activity Detection

Actividades detectables: `walking`, `eating`, `driving`, `shopping`, `swimming`, `talking`, `running`, `cooking`, `touring`.

---

## 22. Environment Detection

Entornos detectables: `street`, `restaurant`, `hotel`, `airport`, `beach`, `museum`, `city`, `nature`, `home`, `office`, `night`.

---

## 23. Location Semantics

Extracción desde metadatos EXIF, nombres de carpeta/archivo, OCR, transcripción o etiquetas explícitas de usuario.

---

## 24. Location Evidence

```typescript
interface LocationCandidate {
  name: string;
  confidence: number;
  source: MetadataSource;
}
```

---

## 25. OCR

Texto visible en letreros, menús, carteles de calles, mapas o pantallas mediante OCR local.

---

## 26. OCR Confidence

El texto reconocido conserva su métrica de confianza; prohibido tomar lecturas dudosas como verdades absolutas.

---

## 27. Transcript Segmentation

El emparejador divide la transcripción en oraciones, cláusulas y segmentos semánticos discretos.

---

## 28. Semantic Segment

```typescript
interface SemanticSegment {
  id: string;
  start: number;
  end: number;
  text: string;
  normalizedText: string;
  language: string;
  keywords: Keyword[];
  entities: EntityMention[];
  intent?: NarrativeIntent;
}
```

---

## 29. Narrative Intent

```typescript
type NarrativeIntent =
  | "LOCATION"
  | "FOOD"
  | "ACTIVITY"
  | "EXPERIENCE"
  | "FACT"
  | "PERSON"
  | "OBJECT"
  | "TRANSITION"
  | "EMOTION"
  | "REFLECTION"
  | "INTRODUCTION"
  | "CONCLUSION"
  | "OTHER";
```

---

## 30. Keyword Extraction

Extracción y ponderación semántica de palabras clave (ej. *"Fuimos al centro histórico de Guadalajara"* $\implies$ `fuimos`, `centro`, `histórico`, `Guadalajara`).

---

## 31. Stop Words

Atenuación ponderada de palabras funcionales (`el`, `la`, `de`, `que`, `y`, `en`) sin suprimirlas si aportan sintaxis.

---

## 32. Named Entities

Detección de entidades nombradas: ubicaciones, personas, restaurantes, marcas y monumentos.

---

## 33. Entity Importance

Las entidades específicas superan a sustantivos genéricos (`"Guadalajara"` pesa más que `"ciudad"`).

---

## 34. Semantic Synonyms

Normalización a conceptos canónicos comunes (`restaurante`, `restaurant`, `comedor` $\implies$ `PLACE_RESTAURANT`).

---

## 35. Multilingual Matching

Cruce semántico entre idiomas (Transcripción: *"I had dinner in the historic center"* $\leftrightarrow$ Asset: `["cena", "restaurante", "centro histórico"]`).

---

## 36. Language-Agnostic Representation

Representación interna basada en IDs conceptuales neutros, no en literales textuales crudos.

---

## 37. Candidate Generation

```typescript
interface BRollCandidate {
  assetId: string;
  segmentId: string;
  score: number;
  reasons: MatchReason[];
}
```

---

## 38. Match Reason

```typescript
interface MatchReason {
  type:
    | "KEYWORD"
    | "ENTITY"
    | "SEMANTIC"
    | "LOCATION"
    | "ACTIVITY"
    | "OBJECT"
    | "TEMPORAL"
    | "VISUAL"
    | "QUALITY"
    | "CONTINUITY";
  score: number;
}
```

---

## 39. Matching Score

Ponderación base:
$$\text{semantic: } 30\%, \; \text{entity: } 20\%, \; \text{visual: } 15\%, \; \text{location: } 10\%, \; \text{activity: } 10\%, \; \text{quality: } 5\%, \; \text{duration: } 5\%, \; \text{continuity: } 5\%$$

---

## 40. Exact Entity Match

Coincidencia exacta de entidad nombrada entre texto y activo produce un impulso positivo mayor (*strong positive*).

---

## 41. Contradiction Penalty

Penalización ante contradicciones temporales o semánticas evidentes (ej. narración dice *"de noche"* y el activo es diurno).

---

## 42. Negative Semantic Match

```typescript
interface SemanticConflict {
  concept: string;
  penalty: number;
}
```

---

## 43. Temporal Relevance

Priorización de activos grabados en franjas temporales coincidentes con la narración (*"ayer"*, *"esta mañana"*).

---

## 44. Geographic Relevance

Bonus significativo cuando el GPS del activo coincide con la ubicación mencionada en el segmento.

---

## 45. Exact Location Bonus

Impulso configurable para coincidencias geográficas exactas.

---

## 46. Unknown Location

La ausencia de geolocalización no penaliza el activo; simplemente prescinde del bonus de ubicación.

---

## 47. Quality Gate

Exclusión de activos cuya calidad técnica no alcance el umbral mínimo ($\text{qualityScore} < \text{minimumQuality}$).

---

## 48. Quality Threshold

Umbral mínimo inicial: $45 / 100$ (configurable).

---

## 49. Duration Gate

El clip debe disponer de duración útil suficiente para el montaje solicitado.

---

## 50. Minimum Usable Duration

$$\text{minimumUsableDuration} = 0.50\text{ s}$$

---

## 51. Preferred B-Roll Duration

Rango recomendado: $1.0\text{ a }6.0\text{ s}$.

---

## 52. Long B-Roll

Clips largos se dividen virtualmente en subsegmentos sin duplicación física del archivo.

---

## 53. Segment Windows

```typescript
interface MediaSubsegment {
  assetId: string;
  start: number;
  end: number;
}
```

---

## 54. Reuse Policy

Reutilización permitida únicamente en contextos narrativos distintos o utilizando ventanas temporales diferentes del clip.

---

## 55. Reuse Penalty

Penalización creciente por cada reutilización acumulada de un mismo activo.

---

## 56. Repeated Shot Prevention

Prohibido repetir el mismo clip o ventana visual en intervalos de tiempo excesivamente cercanos.

---

## 57. Cooldown

```typescript
interface ReusePolicy {
  cooldownSeconds: number;
  maxUsesPerAsset: number;
}
```

---

## 58. Default Cooldown

$$\text{cooldownSeconds} = 20.0\text{ s}$$

---

## 59. Maximum Asset Uses

$$\text{maxUsesPerAsset} = 3$$

---

## 60. Visual Diversity

Favorecer alternancia entre planos generales, medios, primeros planos, planos detalle, tomas estáticas y con movimiento.

---

## 61. Shot Type

```typescript
type ShotScale =
  | "EXTREME_WIDE"
  | "WIDE"
  | "MEDIUM"
  | "CLOSE"
  | "EXTREME_CLOSE"
  | "UNKNOWN";
```

---

## 62. Shot Diversity Penalty

Penalización ante tres o más clips consecutivos con idéntica escala de plano o movimiento de cámara.

---

## 63. Sequence Continuity

Preservación de la coherencia visual evitando saltos temporales incoherentes (día $\to$ noche $\to$ día) sin justificación.

---

## 64. Intentional Contrast

Ruptura de continuidad permitida ante transiciones explícitas o giros de capítulo.

---

## 65. Scene Grouping

Agrupamiento lógico de activos por ubicación, fecha/hora, cámara o estilo visual.

---

## 66. Scene Group

```typescript
interface SceneGroup {
  id: string;
  assetIds: string[];
  dominantLocation?: string;
  dominantTime?: string;
}
```

---

## 67. Group Continuity Bonus

Bonus de fluidez para microsecuencias coherentes de un mismo entorno.

---

## 68. Example

Tomas `street_01`, `street_02`, `market_01`, `market_02` componen un bloque continuo armónico.

---

## 69. Editorial Arc

Conocimiento del arco narrativo: `HOOK`, `SETUP`, `DEVELOPMENT`, `CLIMAX`, `RESOLUTION`, `OUTRO`.

---

## 70. Hook Rules

Prioridad a tomas de alto impacto visual, máxima nitidez y confirmación semántica rápida.

---

## 71. Setup Rules

Prioridad a planos generales de contexto, establecimiento y geolocalización.

---

## 72. Development Rules

Prioridad a soporte visual específico, personas, detalles y actividades concretas.

---

## 73. Climax Rules

Prioridad a planos con alto dinamismo, movimiento pronunciado e impacto emocional.

---

## 74. Resolution Rules

Prioridad a planos amplios, pausados, ambientales y reflexivos.

---

## 75. Narrative Safety

Prohibido insertar B-Roll por simple coincidencia de una palabra suelta si el sentido de la oración resulta contradictorio.

---

## 76. Example of Bad Match

Texto: *"El restaurante estaba cerrado"* $\ne$ Activo: `restaurant_open.mp4` (rechazado a pesar de contener la palabra restaurante).

---

## 77. Negation Detection

Reconocimiento sintáctico de negaciones (`no`, `nunca`, `sin`, `cerrado`, `cancelado`).

---

## 78. Negation Weight

Las palabras negadas penalizan los activos que muestren la afirmación positiva del concepto.

---

## 79. Numeric Matching

Detección de cifras, precios, fechas, distancias y cantidades en el discurso.

---

## 80. Numeric Conflict

Discurso: *"pagamos 500 pesos"* penaliza activos con carteles o etiquetas de *"50 pesos"*.

---

## 81. Currency Matching

Diferenciación estricta de divisas (`MXN`, `USD`, `EUR`, `GBP`, `BRL`).

---

## 82. Time-of-Day Matching

Diferenciación entre mañana, tarde, atardecer y noche.

---

## 83. Weather Matching

Detección y coincidencia climática (`sunny`, `cloudy`, `rain`, `snow`, `storm`).

---

## 84. Person Matching

Vinculación entre menciones de personajes (*"mi hermano"*, *"el chef"*) y pistas de rostros del proyecto.

---

## 85. Person Identity

Identidades faciales restringidas a etiquetas asignadas por el usuario; prohibido inventar identidades.

---

## 86. Privacy

No generar nombres de personas derivados de biometría sin autorización y datos explícitos del proyecto.

---

## 87. Manual Overrides

```json
{
  "segmentId": "seg_12",
  "preferredAssets": [
    "asset_123",
    "asset_456"
  ]
}
```

---

## 88. Forced Asset

Un activo marcado `FORCED` se impone sobre la selección automática salvo invalidez técnica grave.

---

## 89. Forbidden Asset

Un activo marcado `FORBIDDEN` queda permanentemente vetado de la selección.

---

## 90. Preferred Asset

Un activo marcado `PREFERRED` recibe bonificación sustancial sin imposición forzada.

---

## 91. Asset Editorial Status

```typescript
type EditorialStatus =
  | "AUTO"
  | "PREFERRED"
  | "FORCED"
  | "FORBIDDEN";
```

---

## 92. Manual Region Selection

Delimitación manual opcional de intervalo (`assetId`, `start`, `end`).

---

## 93. Candidate Pool

Generación previa de un conjunto acotado de candidatos prometedores para optimizar el cómputo.

---

## 94. Candidate Retrieval

$$\text{Exact entity} \longrightarrow \text{Location} \longrightarrow \text{Concepts} \longrightarrow \text{Visual tags} \longrightarrow \text{Generic similarity}$$

---

## 95. Candidate Pool Size

$$\text{candidatePoolSize} = 20 \quad (\text{configurable})$$

---

## 96. Final Selection

Selección óptima del pool tras evaluar restricciones duras, puntuaciones blandas, penalizaciones y reglas editoriales.

---

## 97. Hard Constraints

Exclusión absoluta ante activos `FORBIDDEN`, corruptos, ausentes, con duración insuficiente o calidad bajo el mínimo crítico.

---

## 98. Soft Constraints

Modulación de puntuación según nitidez, diversidad, continuidad, relevancia y frescura temporal.

---

## 99. Confidence Threshold

Si ningún candidato supera el umbral de confianza, el segmento se mantiene en A-Roll sin B-Roll forzado.

---

## 100. No Forced Bad B-Roll

$$\text{A-Roll puro} > \text{B-Roll irrelevante}$$

---

## 101. Default Match Threshold

$$\text{minimumMatchConfidence} = 0.62$$

---

## 102. A-Roll Visibility

El sistema alterna armónicamente entre `A-Roll puro`, `A-Roll + B-Roll overlay` y `B-Roll pleno`.

---

## 103. B-Roll Coverage

```typescript
interface CoveragePolicy {
  minimumCoverage: number;
  targetCoverage: number;
  maximumCoverage: number;
}
```

---

## 104. Default Coverage

- Mínimo: $15\%$
- Objetivo: $45\%$
- Máximo: $75\%$
(Guía orientativa de densidad, nunca mandato rígido ciego).

---

## 105. Long Monologue Handling

En monólogos prolongados, alternar dinámicamente cortes de apoyo visual para mantener el dinamismo.

---

## 106. B-Roll Insertion Frequency

$$\text{minBrollGapSeconds} = 1.5\text{ s}$$

---

## 107. Maximum Continuous A-Roll

$$\text{maxContinuousARollSeconds} = 8.0\text{ s} \quad (\text{salvo ausencia de B-roll adecuado})$$

---

## 108. Maximum B-Roll Shot

$$\text{maxContinuousBrollSeconds} = 6.0\text{ s}$$

---

## 109. Punch-In Interaction

Provisión de sugerencias de énfasis, cambios de tema y pausas al motor de punch-in dinámico.

---

## 110. Topic Change Detection

```typescript
interface TopicBoundary {
  timestamp: number;
  confidence: number;
}
```

---

## 111. Punch-In Candidate

```typescript
interface PunchInCandidate {
  start: number;
  end: number;
  reason:
    | "TOPIC_CHANGE"
    | "EMPHASIS"
    | "HOOK"
    | "CLIMAX"
    | "REACTION";
  confidence: number;
}
```

---

## 112. B-Roll Timing

Definición precisa del activo fuente, intervalo fuente $[s_{\text{in}}, s_{\text{out}})$ y ventana de destino $[t_{\text{in}}, t_{\text{out}})$.

---

## 113. Editorial Placement

```typescript
interface BrollPlacement {
  segmentId: string;
  assetId: string;
  sourceStart: number;
  sourceEnd: number;
  targetStart: number;
  targetEnd: number;
  score: number;
}
```

---

## 114. Source/Target Separation

Diferenciación estricta entre la línea de tiempo del activo original y la línea de tiempo del proyecto editado.

---

## 115. Speed Adaptation

Las necesidades de aceleración o dilatación temporal se delegan al `VlogAdaptivePacingEngine`.

---

## 116. Source Clip Integrity

El emparejador nunca corta ni muta físicamente los archivos multimedia maestros.

---

## 117. Reframing Handoff

Suministro de punto focal sugerido (`preferredFocalPoint?: { x: number; y: number }`) para el reencuadre vertical.

---

## 118. Face-Aware B-Roll

Utilización del centro del rostro como ancla de reencuadre cuando hay personas en el B-roll.

---

## 119. Composition Safety

Penalización si el sujeto esencial del clip queda fuera de las zonas seguras del formato destino.

---

## 120. Aspect Ratio Compatibility

Evaluación específica de viabilidad para formatos 16:9, 9:16, 1:1, 4:5 y 21:9.

---

## 121. Vertical Compatibility

En formatos verticales (Shorts/Reels) se favorecen planos con sujetos centrados y seguros.

---

## 122. Landscape Compatibility

En formatos panorámicos (16:9) se favorecen tomas abiertas y planos paisajísticos generales.

---

## 123. Multi-Output Planning

Generación de planes de emparejamiento adaptados independientemente por relación de aspecto.

---

## 124. Determinism

$$\text{Mismo manifiesto} + \text{Misma transcripción} + \text{Misma configuración} \implies \text{Idéntico plan editorial}$$

---

## 125. Tie Breaking

Desempate determinista estricto:
1. Prioridad manual
2. Mayor calidad técnica
3. Mayor confianza semántica
4. Menor contador de reutilizaciones
5. Orden lexicográfico del ID de activo

---

## 126. Stable Sorting

Prohibido utilizar el orden aleatorio del sistema de archivos como criterio de desempate.

---

## 127. Match Explanation

Cada decisión registra sus factores explicativos: coincidencia semántica, entidad, calidad y penalizaciones.

---

## 128. Explainability Example

```json
{
  "assetId": "asset_market_01",
  "score": 0.91,
  "reasons": [
    {
      "type": "ENTITY",
      "score": 0.98
    },
    {
      "type": "LOCATION",
      "score": 0.94
    },
    {
      "type": "VISUAL",
      "score": 0.87
    }
  ]
}
```

---

## 129. Editorial Plan

```typescript
interface EditorialPlan {
  segments: EditorialSegment[];
  placements: BrollPlacement[];
  statistics: MatchingStatistics;
}
```

---

## 130. Editorial Segment

```typescript
interface EditorialSegment {
  segmentId: string;
  aRollAssetId?: string;
  brollPlacements: BrollPlacement[];
  punchInCandidates: PunchInCandidate[];
}
```

---

## 131. Statistics

```typescript
interface MatchingStatistics {
  totalSegments: number;
  matchedSegments: number;
  unmatchedSegments: number;
  averageScore: number;
  brollCoverage: number;
  reusedAssets: number;
}
```

---

## 132. Unmatched Segment

Registro del motivo del descarte y mejor candidato no admitido para facilitar el diagnóstico.

---

## 133. Unmatched Reasons

```typescript
type UnmatchedReason =
  | "NO_CANDIDATES"
  | "BELOW_THRESHOLD"
  | "QUALITY"
  | "DURATION"
  | "FORBIDDEN"
  | "CONFLICT"
  | "INSUFFICIENT_EVIDENCE";
```

---

## 134. Review Queue

Derivación de casos ambiguos o de baja certeza a la cola `review-required`.

---

## 135. Review Priority

Prioridad máxima de revisión ante alta importancia narrativa y baja certeza técnica.

---

## 136. Narrative Importance

```typescript
type NarrativeImportance =
  | "LOW"
  | "MEDIUM"
  | "HIGH"
  | "CRITICAL";
```

---

## 137. Critical Segments

Segmentos de importancia crítica emiten advertencia si no encuentran material visual adecuado.

---

## 138. Critical Examples

Revelación de ubicación central, giros dramáticos, productos clave o conclusiones principales.

---

## 139. Contradiction Detector

Auditoría previa a la finalización para interceptar discrepancias semánticas o temporales.

---

## 140. Contradiction Severity

```typescript
type ContradictionSeverity =
  | "INFO"
  | "WARNING"
  | "HIGH"
  | "CRITICAL";
```

---

## 141. Critical Contradiction

Rechazo automático de cualquier asignación marcada con severidad `CRITICAL`.

---

## 142. Repetition Audit

Auditoría para verificar la ausencia de activos repetidos en ventanas de proximidad temporal indebida.

---

## 143. Diversity Audit

Medición de variedad en escalas de plano, movimiento de cámara y ubicaciones representadas.

---

## 144. Temporal Audit

$$\text{targetStart} \ge 0, \quad \text{targetEnd} > \text{targetStart}$$

---

## 145. Overlap Audit

Verificación de que los placements asignados a la misma pista no presenten solapamientos conflictivos.

---

## 146. Source Bounds

$$0 \le \text{sourceStart} < \text{sourceEnd} \le \text{sourceDuration}$$

---

## 147. No Empty Placement

$$\text{sourceEnd} > \text{sourceStart} \quad (\text{duración estrictamente positiva})$$

---

## 148. Precision

Manejo de tiempos en precisión flotante suficiente para sincronización sub-frame.

---

## 149. Test Matrix

Pruebas integrales de: detección A/B-Roll, Action, Timelapse, Screen, cruce de entidades y ubicaciones, negaciones, números, horas, multilingüe, umbrales de calidad, cooldowns, bloqueos manuales (`FORCE`/`FORBIDDEN`), desempates y auditorías de solapamiento.

---

## 150. Property-Based Tests

$$\text{score} \in [0, 1], \quad \text{confidence} \in [0, 1], \quad 0 \le \text{sourceStart} < \text{sourceEnd} \le \text{duration}$$

---

## 151. Determinism Property

$$\text{match}(A) \equiv \text{match}(A) \quad (\text{plan lógico idéntico})$$

---

## 152. No Invalid Selection Property

Prohibida la asignación hacia activos ausentes, corruptos o prohibidos.

---

## 153. No Out-of-Bounds Property

$$\text{sourceEnd} \le \text{sourceDuration}$$

---

## 154. No Overlap Property

$$\text{placement}[i].\text{targetEnd} \le \text{placement}[i+1].\text{targetStart}$$

---

## 155. Manual Override Property

Todo activo `FORCED` válido se incluye obligatoriamente en el plan final.

---

## 156. Forbidden Property

Ningún activo `FORBIDDEN` aparece jamás en el plan automático.

---

## 157. Threshold Property

Si $\text{bestScore} < \text{minimumMatchConfidence}$, el segmento permanece sin B-Roll.

---

## 158. Reuse Property

El contador de usos de un activo se incrementa deterministamente tras cada asignación.

---

## 159. Semantic Regression Tests

Fixtures con casos canónicos de tacos/comida, hotel/llegada, centro histórico/arquitectura y lluvia/clima.

---

## 160. Negative Fixtures

Casos de control negativo (restaurante cerrado $\ne$ restaurante abierto).

---

## 161. Multilingual Fixtures

Fixtures paralelos en español, inglés y portugués recuperando los mismos conceptos canónicos.

---

## 162. Golden Tests

Planes editoriales de referencia bajo control de versiones (`fixtures/golden/`).

---

## 163. Golden Test Policy

Actualización explícita y documentada de archivos dorados ante cambios del algoritmo.

---

## 164. Regression Protection

Cero degradación de determinismo, calidad técnica o invariantes de seguridad temporal.

---

## 165. Performance

Procesamiento eficiente de $100$, $1000$ y $10000$ segmentos sin matrices completas $\mathcal{O}(N \times M)$ innecesarias.

---

## 166. Indexing

```typescript
interface SemanticIndex {
  search(query: SemanticQuery): Promise<IndexedAsset[]>;
}
```

---

## 167. Index Update

Actualizaciones incrementales del índice al modificar activos del proyecto.

---

## 168. Index Persistence

Persistencia local en `.engine/analysis/semantic-index.json`.

---

## 169. Index Version

Registro de esquemas, versiones de embeddings y normalizadores.

---

## 170. Offline Requirement

Emparejamiento y búsqueda 100% offline.

---

## 171. External API Prohibition

Prohibición de llamadas a APIs externas en tiempo de análisis o emparejamiento.

---

## 172. Provider Abstraction

```typescript
interface SemanticProvider {
  embed(text: string): Promise<number[]>;
  similarity(a: number[], b: number[]): number;
}
```

---

## 173. Local Provider

Implementación por defecto mediante `LocalSemanticProvider`.

---

## 174. Embedding Cache

Caché persistente indexada por `textHash + providerVersion + modelVersion`.

---

## 175. No Network Leakage

Prohibida la fuga de textos, miniaturas o metadatos hacia redes públicas en modo offline.

---

## 176. Configuration Schema

```typescript
interface FootageClassifierConfig {
  classificationWeights: Record<string, number>;
  minimumQuality: number;
  minimumMatchConfidence: number;
  candidatePoolSize: number;
  reusePolicy: ReusePolicy;
  coveragePolicy: CoveragePolicy;
  minBrollGapSeconds: number;
  maxContinuousARollSeconds: number;
  maxContinuousBrollSeconds: number;
  enableMultilingualMatching: boolean;
  enableOCR: boolean;
  enableSemanticEmbeddings: boolean;
}
```

---

## 177. Configuration Validation

Validación estricta de rangos de configuración antes de la ejecución.

---

## 178. Weight Validation

Todos los pesos son no negativos ($\ge 0$) y normalizados.

---

## 179. Configuration Reproducibility

Registro de la configuración activa en el manifiesto de la sesión.

---

## 180. Version Compatibility

Rechazo explícito ante esquemas incompatibles (`INCOMPATIBLE_SCHEMA_VERSION`).

---

## 181. Logging

Registro estructurado de segmentId, activo asignado, score y justificación.

---

## 182. Debug Mode

Exportación detallada de candidatos, penalizaciones y rankings en modo depuración.

---

## 183. Candidate Debug Example

```json
{
  "segmentId": "seg_14",
  "candidates": [
    {
      "assetId": "asset_01",
      "score": 0.91
    },
    {
      "assetId": "asset_08",
      "score": 0.73
    }
  ],
  "selected": "asset_01"
}
```

---

## 184. Explainability Requirement

Toda asignación automática es reproducible a partir de entradas, configuración y modelos locales.

---

## 185. No Hidden Editorial Decisions

Prohibición de números mágicos embebidos en el código.

---

## 186. Constants

Constantes centralizadas en `classifier.constants.ts`.

---

## 187. No Magic Numbers

Uso de propiedades declarativas (`config.minimumMatchConfidence`), nunca literales dispersos.

---

## 188. Module Boundary

Aislamiento total respecto a After Effects, síntesis TTS y renderizado final.

---

## 189. Output Boundary

El resultado es un plan editorial declarativo (`EditorialPlan`), no código ejecutable JSX o proyectos binarios.

---

## 190. Main API

```typescript
interface VlogFootageClassifier {
  classify(manifest: IngestionManifest): Promise<ClassificationRegistry>;
}
```

---

## 191. Main Matcher API

```typescript
interface BRollMatcher {
  match(
    transcript: Transcript,
    registry: ClassificationRegistry,
    config: FootageClassifierConfig
  ): Promise<EditorialPlan>;
}
```

---

## 192. Validation API

```typescript
interface EditorialPlanValidator {
  validate(plan: EditorialPlan): ValidationReport;
}
```

---

## 193. Validation Report

```typescript
interface ValidationReport {
  valid: boolean;
  errors: ValidationIssue[];
  warnings: ValidationIssue[];
}
```

---

## 194. Pipeline Contract

```
INGESTION
    ↓
CLASSIFICATION
    ↓
SEMANTIC INDEX
    ↓
TRANSCRIPT
    ↓
B-ROLL MATCHING
    ↓
EDITORIAL PLAN
    ↓
JUMP CUT
    ↓
PUNCH-IN
    ↓
PACING
    ↓
LOCALIZATION
    ↓
OVERLAYS
    ↓
AFTER EFFECTS JSX
```

---

## 195. Definition of Done

- [ ] Footage type classification
- [ ] Confidence scores
- [ ] Classification explanations
- [ ] A-Roll scoring
- [ ] B-Roll scoring
- [ ] Action detection
- [ ] Timelapse detection
- [ ] Screen detection
- [ ] Semantic tagging
- [ ] Object concepts
- [ ] Activity concepts
- [ ] Environment concepts
- [ ] Location candidates
- [ ] OCR integration point
- [ ] Transcript segmentation
- [ ] Keyword extraction
- [ ] Entity extraction
- [ ] Narrative intent
- [ ] Multilingual concepts
- [ ] Semantic candidate retrieval
- [ ] Match scoring
- [ ] Contradiction detection
- [ ] Negation handling
- [ ] Numeric handling
- [ ] Location matching
- [ ] Temporal matching
- [ ] Quality gates
- [ ] Duration gates
- [ ] Asset reuse policy
- [ ] Cooldown
- [ ] Diversity
- [ ] Continuity
- [ ] Hook rules
- [ ] Climax rules
- [ ] Resolution rules
- [ ] Manual overrides
- [ ] Forced assets
- [ ] Forbidden assets
- [ ] Preferred assets
- [ ] Candidate pool
- [ ] Deterministic ranking
- [ ] Tie breaking
- [ ] Explainability
- [ ] Unmatched handling
- [ ] Review queue
- [ ] Multi-aspect support
- [ ] Offline operation
- [ ] Provider abstraction
- [ ] Semantic cache
- [ ] Configuration validation
- [ ] Golden tests
- [ ] Property-based tests
- [ ] Regression tests
- [ ] Performance benchmarks
- [ ] Plan validation

---

## 196. Estado

**Documento:** `15-VLOG-FOOTAGE-CLASSIFIER-A-ROLL-B-ROLL-MATCHER.md`  
**Versión:** `1.0.0`  
**Estado:** `DRAFT`  
**Implementación autorizada:** `NO`  

---

## 197. Regla de Implementación

Este documento define la clasificación y selección editorial de material. No deberá implementar dentro de este módulo jump cuts definitivos, time-stretching, TTS, traducción, mezcla de audio, overlays finales, render ni exportación a After Effects.

El output debe ser un plan declarativo que permita a los módulos posteriores ejecutar la edición sin volver a tomar decisiones semánticas fundamentales.
