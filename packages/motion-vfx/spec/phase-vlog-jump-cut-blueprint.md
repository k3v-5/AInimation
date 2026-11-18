# 📐 BLUEPRINT TÉCNICO DEFINITIVO: FASE 1 — VLOG JUMP CUT ENGINE & DYNAMIC PUNCH-IN (v3.5.0)

**Documento de Especificación Ejecutable para Implementación de Software**  
**Capa Arquitectónica:** `v3.5.x Vlog Intelligence Layer`  
**Módulo:** `src/automation/vlog/jump-cut/`  
**Estado:** `LISTO PARA IMPLEMENTACIÓN (TDD OBLIGATORIO)`  

---

## 📑 ÍNDICE DE SECCIONES

1. [Objetivo y Alcance del Módulo](#1-objetivo-y-alcance-del-módulo)
2. [Estructura de Archivos del Módulo](#2-estructura-de-archivos-del-módulo)
3. [Interfaces TypeScript Definitivas (`types.ts`)](#3-interfaces-typescript-definitivas-typests)
4. [Configuración y Parámetros Inmutables (`config.ts`)](#4-configuración-y-parámetros-inmutables-configts)
5. [Modelo de Errores Tipados (`errors.ts`)](#5-modelo-de-errores-tipados-errorsts)
6. [Algoritmo Matemático Paso a Paso (`VlogJumpCutEngine.ts`)](#6-algoritmo-matemático-paso-a-paso-vlogjumpcutenginets)
7. [Contrato y Algoritmo de Dynamic Punch-In (`DynamicPunchIn.ts`)](#7-contrato-y-algoritmo-de-dynamic-punch-in-dynamicpunchints)
8. [Definición de Fixtures de Prueba (`fixtures/`)](#8-definición-de-fixtures-de-prueba-fixtures)
9. [Diseño Exhaustivo de la Suite de Pruebas (TDD)](#9-diseño-exhaustivo-de-la-suite-de-pruebas-tdd)
10. [Plan de Integración y Criterios de Aceptación (Gate Final)](#10-plan-de-integración-y-criterios-de-aceptación-gate-final)

---

## 1. Objetivo y Alcance del Módulo

### 1.1. Qué HACE este módulo
- Recibe metadatos de audio (silencios candidatos y perfil de energía) y transcripción con marcas de tiempo a nivel de palabra.
- Detecta y remueve silencios estrictamente mayores a $0.250\text{s}$ ($250\text{ms}$).
- Protege las palabras habladas aplicando un margen de seguridad (*padding*) de $40\text{ms}$ pre/post por palabra para no mutilar consonantes ni ataques vocales.
- Genera micro-crossfades de audio de $10\text{ms}$ con protección adaptativa anti-solapamiento destructivo.
- Dispara eventos de **Dynamic Punch-In** ($100\% \to 115\% \to 100\%$) gatillados por eventos editoriales (picos de energía $\ge 0.70$ o palabras de énfasis), con cooldown mínimo para evitar saltos absurdos.
- Produce un **`VlogJumpCutResult`** declarativo, serializable y 100% determinista.

### 1.2. Qué NO HACE este módulo
- NO muta ni reemplaza el core existente de v3.4.0.
- NO renderiza vídeo directamente ni llama a procesos externos durante el análisis.
- NO contiene heurísticas mágicas embebidas sin parametrizar.
- NO depende de APIs cloud de pago ni llamadas de red.

---

## 2. Estructura de Archivos del Módulo

```
src/
└── automation/
    └── vlog/
        └── jump-cut/
            ├── types.ts              # Contratos de datos e interfaces
            ├── config.ts             # Parámetros y valores por defecto (cero magic numbers)
            ├── errors.ts             # Jerarquía de errores tipados
            ├── DynamicPunchIn.ts     # Cálculo de punch-ins editoriales y FocusPoints
            ├── VlogJumpCutEngine.ts  # Orquestador y planificador editorial
            └── index.ts              # Exportaciones públicas

src/
└── tests/
    └── automation/
        └── vlog/
            └── jump-cut/
                ├── boundaries.test.ts        # Casos límite (0ms, 249ms, 250ms, 251ms, etc.)
                ├── DynamicPunchIn.test.ts    # Pruebas unitarias de punch-in
                ├── VlogJumpCutEngine.test.ts # Pruebas funcionales e integración
                ├── property-based.test.ts    # Pruebas generativas PBT con fast-check
                └── fixtures/
                    └── golden-vlog-input.json # Fixture golden determinista
```

---

## 3. Interfaces TypeScript Definitivas (`types.ts`)

```typescript
export interface FocusPoint {
  readonly x: number; // Normalizado: 0.0 (izquierda) a 1.0 (derecha)
  readonly y: number; // Normalizado: 0.0 (arriba) a 1.0 (abajo)
}

export interface MediaReference {
  readonly id: string;
  readonly filePath: string;
  readonly durationSec: number;
}

export interface AudioSamplePoint {
  readonly timestamp: number;
  readonly rms: number; // Normalizado: 0.0 a 1.0
  readonly dbfs?: number;
}

export interface CandidateSilence {
  readonly start: number;
  readonly end: number;
  readonly duration: number;
}

export interface WordBoundary {
  readonly id?: string;
  readonly text: string;
  readonly start: number;
  readonly end: number;
  readonly confidence?: number;
}

export interface AudioAnalysis {
  readonly silences: CandidateSilence[];
  readonly energyProfile?: AudioSamplePoint[];
  readonly sampleRate?: number;
}

export interface TranscriptAnalysis {
  readonly words: WordBoundary[];
  readonly language?: string;
}

export interface SilenceSegment {
  readonly start: number;
  readonly end: number;
  readonly duration: number;
  readonly reason: "silence_greater_than_threshold";
}

export type PunchInTriggerReason =
  | "emphasis"
  | "sentence_boundary"
  | "energy_climax"
  | "manual";

export interface PunchInEvent {
  readonly start: number;
  readonly end: number;
  readonly scale: number;
  readonly focusPoint: FocusPoint;
  readonly reason: PunchInTriggerReason;
}

export interface AudioCrossfadeSpec {
  readonly fadeInStart: number;
  readonly fadeInEnd: number;
  readonly fadeOutStart: number;
  readonly fadeOutEnd: number;
  readonly durationSec: number; // Típicamente 0.010 s
}

export interface VlogEditSegment {
  readonly id: string;
  readonly sourceStart: number;
  readonly sourceEnd: number;
  readonly sourceDuration: number;
  readonly outputStart: number;
  readonly outputEnd: number;
  readonly outputDuration: number;
  readonly scale: number;
  readonly focusPoint: FocusPoint;
  readonly audioCrossfade?: AudioCrossfadeSpec;
}

export interface JumpCutStatistics {
  readonly originalDurationSec: number;
  readonly editedDurationSec: number;
  readonly savedTimeSec: number;
  readonly compressionRatioPct: number;
  readonly totalCuts: number;
  readonly totalPunchIns: number;
  readonly preservedWordsCount: number;
}

export interface VlogJumpCutInput {
  readonly source: MediaReference;
  readonly audio: AudioAnalysis;
  readonly transcript?: TranscriptAnalysis;
  readonly config?: Partial<VlogJumpCutConfig>;
}

export interface VlogJumpCutResult {
  readonly sourceDuration: number;
  readonly outputDuration: number;
  readonly segments: VlogEditSegment[];
  readonly removedSilences: SilenceSegment[];
  readonly punchIns: PunchInEvent[];
  readonly statistics: JumpCutStatistics;
}
```

---

## 4. Configuración y Parámetros Inmutables (`config.ts`)

```typescript
import { FocusPoint } from "./types.js";

export interface VlogJumpCutConfig {
  readonly silenceThresholdSec: number;        // 0.250 s (250 ms)
  readonly crossfadeDurationSec: number;       // 0.010 s (10 ms)
  readonly wordSafetyPaddingSec: number;       // 0.040 s (40 ms pre y post palabra)
  readonly normalScale: number;                // 1.00
  readonly punchInScale: number;               // 1.15
  readonly minSpeechSegmentDurationSec: number;  // 0.150 s (150 ms)
  readonly minPunchInDurationSec: number;        // 1.20 s
  readonly maxPunchInDurationSec: number;        // 6.00 s
  readonly punchInCooldownSec: number;           // 2.50 s
  readonly punchInEnergyThreshold: number;     // 0.70 (RMS)
  readonly defaultFocusPoint: FocusPoint;      // { x: 0.5, y: 0.5 }
  readonly deterministicSeed: number;          // 42
}

export const DEFAULT_VLOG_JUMP_CUT_CONFIG: VlogJumpCutConfig = Object.freeze({
  silenceThresholdSec: 0.250,
  crossfadeDurationSec: 0.010,
  wordSafetyPaddingSec: 0.040,
  normalScale: 1.0,
  punchInScale: 1.15,
  minSpeechSegmentDurationSec: 0.150,
  minPunchInDurationSec: 1.20,
  maxPunchInDurationSec: 6.00,
  punchInCooldownSec: 2.50,
  punchInEnergyThreshold: 0.70,
  defaultFocusPoint: Object.freeze({ x: 0.5, y: 0.5 }),
  deterministicSeed: 42,
});
```

---

## 5. Modelo de Errores Tipados (`errors.ts`)

```typescript
import { MotionEngineError } from "../../../errors/index.js";

export class VlogJumpCutError extends MotionEngineError {
  constructor(message: string, public readonly code: string, public readonly context?: Record<string, any>) {
    super(`[VlogJumpCutEngine:${code}] ${message}`);
  }
}

export class InvalidMediaReferenceError extends VlogJumpCutError {
  constructor(reason: string, context?: Record<string, any>) {
    super(`Invalid MediaReference: ${reason}`, "INVALID_MEDIA_REFERENCE", context);
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
      `Crossfade duration (${crossfadeDuration}s) exceeds safe threshold of segment duration (${segmentDuration}s)`,
      "CROSSFADE_OVERLAP",
      { crossfadeDuration, segmentDuration }
    );
  }
}
```

---

## 6. Algoritmo Matemático Paso a Paso (`VlogJumpCutEngine.ts`)

```
ENTRADA: VlogJumpCutInput (source, audio, transcript?, config?)
  │
  ├─ 1. Validación de Entrada
  │      Verificar source.durationSec > 0.
  │      Verificar orden de silencias y timestamps >= 0.
  │
  ├─ 2. Normalización de Silencios Candidatos
  │      Ordenar silencios por start ascendente.
  │      Fusionar silencios solapados o contiguos.
  │
  ├─ 3. Aplicación del Filtro de Palabra (Transcript Boundary Check)
  │      Para cada silencio candidato [S_start, S_end):
  │        Si existe transcript:
  │          Calcular zonas protegidas [W_start - 0.040s, W_end + 0.040s] para cada palabra.
  │          Recortar [S_start, S_end) restando las zonas protegidas.
  │
  ├─ 4. Regla Estricta del Silencio
  │      Silencio es REMOVIBLE <=> (S_end - S_start) > silenceThresholdSec (estrictamente > 0.250s).
  │      Si <= 0.250s -> Conservar en el timeline.
  │
  ├─ 5. Construcción de Segmentos de Voz Útiles (Source Segments)
  │      Invertir los silencios eliminados respecto a [0, sourceDuration].
  │      Generar segmentos válidos [srcStart, srcEnd).
  │      Descartar segmentos con duración < minSpeechSegmentDurationSec (0.150s) si son ruido.
  │
  ├─ 6. Cálculo de Dynamic Punch-In
  │      Invocar DynamicPunchIn.calculatePunchIns(segments, audio.energyProfile, transcript, config).
  │      Asignar scale = 1.15 a segmentos que caen dentro de un PunchInEvent, y 1.00 al resto.
  │
  ├─ 7. Cálculo de Micro-Crossfades de Audio
  │      Para cada corte entre segmento i y i+1:
  │        effectiveFade = min(crossfadeDurationSec, dur(i)/2, dur(i+1)/2).
  │        Generar AudioCrossfadeSpec con rampas de fade.
  │
  ├─ 8. Mapeo a Línea de Salida (Output Continuity)
  │      currentOutput = 0.0
  │      Para cada segmento i:
  │        outputStart = currentOutput
  │        outputEnd = currentOutput + sourceDuration_i
  │        currentOutput = outputEnd
  │
  └─ 9. Retorno de VlogJumpCutResult y Estadísticas
```

---

## 7. Contrato y Algoritmo de Dynamic Punch-In (`DynamicPunchIn.ts`)

```typescript
export class DynamicPunchIn {
  /**
   * Calcula eventos editoriales de punch-in (escala 1.15) basados en picos de energía o énfasis.
   */
  public static calculatePunchIns(
    segments: Array<{ start: number; end: number; duration: number }>,
    energyProfile: AudioSamplePoint[] = [],
    transcript?: TranscriptAnalysis,
    config: VlogJumpCutConfig = DEFAULT_VLOG_JUMP_CUT_CONFIG
  ): PunchInEvent[] {
    const punchIns: PunchInEvent[] = [];
    if (segments.length === 0) return punchIns;

    let lastPunchInEnd = -config.punchInCooldownSec;

    for (let i = 0; i < segments.length; i++) {
      const seg = segments[i];

      // Verificar cooldown para no saturar con punch-ins seguidos
      if (seg.start - lastPunchInEnd < config.punchInCooldownSec) {
        continue;
      }

      // 1. Detección por pico de energía
      const samplesInSeg = energyProfile.filter(
        s => s.timestamp >= seg.start && s.timestamp <= seg.end
      );
      const maxEnergy = samplesInSeg.length > 0 ? Math.max(...samplesInSeg.map(s => s.rms)) : 0;
      const isHighEnergy = maxEnergy >= config.punchInEnergyThreshold;

      // 2. Detección por palabra clave / pregunta en transcript
      let isEmphasisWord = false;
      if (transcript) {
        const wordsInSeg = transcript.words.filter(
          w => w.start >= seg.start && w.end <= seg.end
        );
        isEmphasisWord = wordsInSeg.some(
          w => w.text.includes("?") || w.text.includes("!") || w.text.toUpperCase() === w.text && w.text.length > 3
        );
      }

      if (isHighEnergy || isEmphasisWord) {
        const targetDuration = Math.min(
          config.maxPunchInDurationSec,
          Math.max(config.minPunchInDurationSec, seg.duration)
        );
        const pEnd = Math.min(seg.start + targetDuration, seg.end);

        punchIns.push({
          start: Number(seg.start.toFixed(3)),
          end: Number(pEnd.toFixed(3)),
          scale: config.punchInScale,
          focusPoint: config.defaultFocusPoint,
          reason: isHighEnergy ? "energy_climax" : "emphasis",
        });

        lastPunchInEnd = pEnd;
      }
    }

    return punchIns;
  }
}
```

---

## 8. Definición de Fixtures de Prueba (`fixtures/`)

### `fixtures/golden-vlog-input.json`
```json
{
  "source": {
    "id": "vlog_guadalajara_01",
    "filePath": "C:/Footage/Guadalajara_Day1.mp4",
    "durationSec": 20.0
  },
  "audio": {
    "silences": [
      { "start": 0.0, "end": 1.2, "duration": 1.2 },
      { "start": 4.5, "end": 4.749, "duration": 0.249 },
      { "start": 4.749, "end": 5.0, "duration": 0.251 },
      { "start": 8.0, "end": 8.250, "duration": 0.250 },
      { "start": 8.250, "end": 8.501, "duration": 0.251 },
      { "start": 18.5, "end": 20.0, "duration": 1.5 }
    ],
    "energyProfile": [
      { "timestamp": 2.5, "rms": 0.85 },
      { "timestamp": 6.5, "rms": 0.40 },
      { "timestamp": 12.0, "rms": 0.92 }
    ]
  },
  "transcript": {
    "words": [
      { "text": "Hola", "start": 1.3, "end": 1.7 },
      { "text": "amigos,", "start": 1.75, "end": 2.3 },
      { "text": "¡INCREÍBLE!", "start": 2.35, "end": 3.2 },
      { "text": "estamos", "start": 3.3, "end": 3.8 },
      { "text": "en", "start": 3.85, "end": 4.1 },
      { "text": "Guadalajara", "start": 4.15, "end": 4.45 },
      { "text": "caminando", "start": 5.1, "end": 5.8 },
      { "text": "por", "start": 5.85, "end": 6.1 },
      { "text": "el", "start": 6.15, "end": 6.3 },
      { "text": "centro.", "start": 6.35, "end": 7.8 },
      { "text": "¿Vieron", "start": 8.6, "end": 9.1 },
      { "text": "eso?", "start": 9.15, "end": 9.6 }
    ]
  }
}
```

---

## 9. Diseño Exhaustivo de la Suite de Pruebas (TDD)

### 9.1. `boundaries.test.ts` (Pruebas de Límites Matemáticos)
- `silence_0ms`: Silencio de $0\text{ms}$ no se elimina.
- `silence_1ms`: Silencio de $1\text{ms}$ no se elimina.
- `silence_249ms`: Silencio de $0.249\text{s}$ no se elimina.
- `silence_250ms`: Silencio de $0.250\text{s}$ exacto no se elimina ($\le 0.250$).
- `silence_251ms`: Silencio de $0.251\text{s}$ **se elimina** ($> 0.250$).
- `silence_500ms`: Silencio de $0.500\text{s}$ se elimina.
- `silence_at_start`: Silencio en $t=0.0$.
- `silence_at_end`: Silencio en $t=\text{sourceDuration}$.

### 9.2. `DynamicPunchIn.test.ts` (Pruebas de Punch-In)
- Escala normal $1.00$ y escala punch-in $1.15$.
- Disparo por `energy_climax` ($\text{RMS} \ge 0.70$).
- Disparo por `emphasis` (palabras con `!` o `?`).
- Respeto estricto del cooldown de $2.5\text{s}$ entre punch-ins consecutivos.
- `FocusPoint` siempre acotado en $[0.0, 1.0]$.

### 9.3. `VlogJumpCutEngine.test.ts` (Pruebas Funcionales)
- Protección de palabras con $40\text{ms}$ de colchón sin mutilación de texto.
- Descarte de silencios falsos dentro de palabras.
- Micro-crossfade de audio de $10\text{ms}$ en cada unión.
- Continuidad perfecta $\text{outputStart}_{i+1} == \text{outputEnd}_i$.
- $\text{outputDuration} \le \text{sourceDuration}$.
- Determinismo: 100 ejecuciones sucesivas devuelven la misma estructura exacta.

### 9.4. `property-based.test.ts` (`fast-check` Generativo)
- Generación de 100 timelines aleatorios:
  $$\forall \text{ timeline válido}: \text{outputStart}_{i+1} \ge \text{outputEnd}_i \land \text{outputDuration} \ge 0 \land \text{outputDuration} \le \text{sourceDuration}$$

---

## 10. Plan de Integración y Criterios de Aceptación (Gate Final)

### 10.1. Criterio de Aceptación Obligatorio (Gate de Fase 1)
```
┌────────────────────────────────────────────────────────┐
│         CRITERIO DE APROBACIÓN DE FASE 1               │
├────────────────────────────────────────────────────────┤
│ ✅ 712 / 712 tests existentes en verde (0 regresiones)  │
│ ✅ 100% de tests nuevos de jump-cut en verde           │
│ ✅ Property-Based Tests (fast-check) 100% PASS         │
│ ✅ Golden Fixture hash verificado                      │
│ ✅ TypeScript sin errores de compilación (`tsc`)       │
│ ✅ Registro en `docs/POST_PHASE_IMPROVEMENTS.md` (#033)│
│ ✅ Cero magic numbers en el código                     │
│ ✅ Cero dependencias de APIs externas                  │
└────────────────────────────────────────────────────────┘
```
