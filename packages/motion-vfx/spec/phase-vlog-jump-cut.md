# Especificación Técnica & Blueprint de Implementación: Fase 1 — VlogJumpCutEngine (v3.5.0)

Este documento define el contrato formal, tipos, algoritmos, invariantes, manejo de errores y batería de tests requeridos para la implementación de **`VlogJumpCutEngine`** en `src/automation/vlog/jump-cut/`.

---

## 1. Arquitectura y Ubicación de Archivos

```
src/automation/vlog/jump-cut/
├── types.ts              # Interfaces y contratos de datos
├── config.ts             # Configuración y valores por defecto (cero magic numbers)
├── errors.ts             # Jerarquía de errores tipados
├── DynamicPunchIn.ts     # Cálculo de eventos de punch-in (100% -> 115% -> 100%)
├── VlogJumpCutEngine.ts  # Orquestador del análisis y generación de VlogEditPlan
└── index.ts              # Exportaciones públicas

src/tests/automation/vlog/jump-cut/
├── VlogJumpCutEngine.test.ts # Tests funcionales y unitarios de integración
├── DynamicPunchIn.test.ts    # Tests del detector de punch-ins y focus points
├── boundaries.test.ts        # Tests exhaustivos de límites temporales (0ms, 249ms, 250ms, 251ms)
├── property-based.test.ts    # Tests generativos con fast-check (invariantes matemáticos)
└── fixtures/
    └── golden-vlog-input.json # Fixture golden determinista
```

---

## 2. Definición de Tipos e Interfaces (`types.ts`)

```typescript
export interface FocusPoint {
  x: number; // Normalizado 0.0 (izquierda) a 1.0 (derecha)
  y: number; // Normalizado 0.0 (arriba) a 1.0 (abajo)
}

export interface MediaReference {
  id: string;
  filePath: string;
  durationSec: number;
}

export interface AudioSamplePoint {
  timestamp: number;
  rms: number; // 0.0 a 1.0
  dbfs?: number;
}

export interface CandidateSilence {
  start: number;
  end: number;
  duration: number;
}

export interface WordBoundary {
  id?: string;
  text: string;
  start: number;
  end: number;
  confidence?: number;
}

export interface AudioAnalysis {
  silences: CandidateSilence[];
  energyProfile?: AudioSamplePoint[];
  sampleRate?: number;
}

export interface TranscriptAnalysis {
  words: WordBoundary[];
  language?: string;
}

export interface SilenceSegment {
  start: number;
  end: number;
  duration: number;
  reason: "silence_greater_than_threshold";
}

export interface PunchInEvent {
  start: number;
  end: number;
  scale: number;
  focusPoint: FocusPoint;
  reason: "emphasis" | "sentence_boundary" | "energy_climax" | "manual";
}

export interface AudioCrossfadeSpec {
  fadeInStart: number;
  fadeInEnd: number;
  fadeOutStart: number;
  fadeOutEnd: number;
  durationSec: number; // 0.010 s por defecto
}

export interface VlogEditSegment {
  id: string;
  sourceStart: number;
  sourceEnd: number;
  sourceDuration: number;
  outputStart: number;
  outputEnd: number;
  outputDuration: number;
  scale: number;
  focusPoint: FocusPoint;
  audioCrossfade?: AudioCrossfadeSpec;
}

export interface JumpCutStatistics {
  originalDurationSec: number;
  editedDurationSec: number;
  savedTimeSec: number;
  compressionRatioPct: number;
  totalCuts: number;
  totalPunchIns: number;
  preservedWordsCount: number;
}

export interface VlogJumpCutInput {
  source: MediaReference;
  audio: AudioAnalysis;
  transcript?: TranscriptAnalysis;
  config?: Partial<VlogJumpCutConfig>;
}

export interface VlogJumpCutResult {
  sourceDuration: number;
  outputDuration: number;
  segments: VlogEditSegment[];
  removedSilences: SilenceSegment[];
  punchIns: PunchInEvent[];
  statistics: JumpCutStatistics;
}
```

---

## 3. Configuración y Parámetros (`config.ts`)

```typescript
export interface VlogJumpCutConfig {
  readonly silenceThresholdSec: number;       // Estrictamente 0.25 s
  readonly crossfadeDurationSec: number;      // 0.010 s (10 ms)
  readonly wordSafetyPaddingSec: number;      // 0.040 s (40 ms pre/post para plosivas)
  readonly normalScale: number;               // 1.00
  readonly punchInScale: number;              // 1.15
  readonly minSpeechSegmentDurationSec: number; // 0.150 s
  readonly punchInEnergyThreshold: number;    // 0.70
  readonly defaultFocusPoint: FocusPoint;     // { x: 0.5, y: 0.5 }
  readonly deterministicSeed: number;         // 42
}

export const DEFAULT_VLOG_JUMP_CUT_CONFIG: VlogJumpCutConfig = {
  silenceThresholdSec: 0.25,
  crossfadeDurationSec: 0.010,
  wordSafetyPaddingSec: 0.040,
  normalScale: 1.0,
  punchInScale: 1.15,
  minSpeechSegmentDurationSec: 0.150,
  punchInEnergyThreshold: 0.70,
  defaultFocusPoint: { x: 0.5, y: 0.5 },
  deterministicSeed: 42,
};
```

---

## 4. Jerarquía de Errores Tipados (`errors.ts`)

```typescript
import { MotionEngineError } from "../../../errors/index.js";

export class VlogJumpCutError extends MotionEngineError {
  constructor(message: string, public readonly code: string, public readonly context?: Record<string, any>) {
    super(`[VlogJumpCutEngine:${code}] ${message}`);
  }
}

export class InvalidTimeRangeError extends VlogJumpCutError {
  constructor(start: number, end: number, reason: string) {
    super(`Invalid time range [${start}, ${end}): ${reason}`, "INVALID_TIME_RANGE", { start, end, reason });
  }
}

export class CrossfadeOverlapError extends VlogJumpCutError {
  constructor(crossfadeDuration: number, segmentDuration: number) {
    super(
      `Crossfade duration (${crossfadeDuration}s) exceeds half of segment duration (${segmentDuration}s)`,
      "CROSSFADE_OVERLAP",
      { crossfadeDuration, segmentDuration }
    );
  }
}

export class TranscriptAlignmentError extends VlogJumpCutError {
  constructor(message: string, context?: Record<string, any>) {
    super(message, "TRANSCRIPT_ALIGNMENT_ERROR", context);
  }
}
```

---

## 5. Algoritmo Paso a Paso e Invariantes Críticos

### Invariante 1: Regla de Eliminación de Silencios
Un candidato a silencio $[t_{\text{start}}, t_{\text{end}})$ es elegible para eliminación **únicamente** si:
$$\text{duration} = (t_{\text{end}} - t_{\text{start}}) > \text{silenceThresholdSec} \quad (\text{estrictamente } > 0.250\text{s})$$

### Invariante 2: Protección Estricta de Palabras
Si se provee `transcript`, ningún corte puede ocurrir dentro de una palabra ni dentro del margen de seguridad:
$$[w_{\text{start}} - \text{wordSafetyPaddingSec}, \; w_{\text{end}} + \text{wordSafetyPaddingSec}]$$
Si un candidato a silencio intersecta con una palabra protegida, el silencio se contrae o se descarta.

### Invariante 3: Micro-Crossfade de Audio
Para cada unión entre el segmento $i$ y el segmento $i+1$:
$$\text{effectiveFade} = \min\left(\text{crossfadeDurationSec}, \frac{\text{duration}(S_i)}{2}, \frac{\text{duration}(S_{i+1})}{2}\right)$$

### Invariante 4: Punch-Ins Basados en Eventos Editoriales
El módulo `DynamicPunchIn` evalúa:
1. Picos de energía acústica $\ge \text{punchInEnergyThreshold}$.
2. Palabras de énfasis o inicio de nuevas ideas/preguntas.
3. Al detectarse, se activa `scale = punchInScale` ($1.15$). En el siguiente corte editorial o pausa de frase, retorna a `normalScale` ($1.00$).

### Invariante 5: Continuidad y No-Solapamiento en la Línea de Salida
Para toda la secuencia generada:
$$\text{outputStart}_{i+1} = \text{outputEnd}_i$$
$$\text{outputEnd}_i - \text{outputStart}_i = \text{sourceEnd}_i - \text{sourceStart}_i$$
$$\text{outputDuration} = \sum (\text{sourceEnd}_i - \text{sourceStart}_i) \le \text{sourceDuration}$$

---

## 6. Batería de Pruebas de 7 Capas Obligatoria

1. **Boundary Tests (`boundaries.test.ts`):**
   - Silencio $0\text{ms}$ $\to$ Preservar.
   - Silencio $1\text{ms}$ $\to$ Preservar.
   - Silencio $249\text{ms}$ ($0.249\text{s}$) $\to$ Preservar.
   - Silencio $250\text{ms}$ ($0.250\text{s}$) $\to$ Preservar.
   - Silencio $251\text{ms}$ ($0.251\text{s}$) $\to$ **Eliminar**.
   - Silencio al inicio exacto ($t=0$).
   - Silencio al final exacto ($t=\text{sourceDuration}$).
2. **Word Protection Tests (`VlogJumpCutEngine.test.ts`):**
   - Silencio entre palabras con $40\text{ms}$ de colchón sin mutilar fonemas.
   - Descarte de silencios falsos que caen dentro del cuerpo de una palabra.
3. **Crossfade Tests (`boundaries.test.ts`):**
   - Longitud de fade exactamente $0.010\text{s}$.
   - Reducción adaptativa segura cuando el segmento es menor a $20\text{ms}$.
4. **Punch-In Tests (`DynamicPunchIn.test.ts`):**
   - Transición de escala $1.00 \to 1.15 \to 1.00$.
   - Focus point siempre normalizado en $[0.0, 1.0]$.
5. **Property-Based Tests (`property-based.test.ts` con `fast-check`):**
   - Generación de 100 timelines sintéticos aleatorios:
     - No solapamiento en salida: $\text{outputStart}_{i+1} \ge \text{outputEnd}_i$.
     - $\text{outputDuration} \ge 0$.
     - $\text{outputDuration} \le \text{sourceDuration}$.
6. **Golden Determinism Test:**
   - 100 ejecuciones sucesivas del mismo fixture producen el mismo hash/estructura `deepStrictEqual`.
7. **Regresión:**
   - **712/712 pruebas existentes de v3.4.0 deben permanecer 100% en verde.**
