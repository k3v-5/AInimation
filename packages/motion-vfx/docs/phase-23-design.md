# Documento de Diseño Técnico: Fase 23 — Perceptual QA, Visual Intelligence & Render Validation (v2.3.0)

## 1. Arquitectura de Separación de 3 Niveles

```
┌─────────────────────────────────────────────────────────────┐
│                 NIVEL 1 — DECLARATIVO (IR)                  │
│       (Composition, Layers, Timeline, Captions, Audio)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  NIVEL 2 — EVALUACIÓN (t)                   │
│             (Composition.evaluate(t) -> FrameState)         │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                 NIVEL 3 — PERCEPCIÓN & QA                   │
│ (Visual, Typography, Motion, Audio, Temporal Continuity)    │
│           -> PerceptualObservations & Evidence              │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                 PERCEPTUAL REPAIR & RE-QA                   │
│    (PerceptualRepairMapper -> ChangeSet -> RevisionEngine)  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Contratos y Modelos de Datos

### 2.1 `PerceptualObservation`
```typescript
export interface PerceptualObservation {
  id: string; // "obs_" + 16 hex
  revisionId: string;
  time: number;
  category: "visual" | "typography" | "composition" | "motion" | "audio" | "caption" | "temporal";
  metric: string;
  value: number;
  normalizedValue: number; // 0..100
  threshold?: number;
  status: "pass" | "warning" | "fail";
  confidence: number;
  evidence?: Record<string, unknown>;
}
```

### 2.2 `PerceptualIssue`
```typescript
export interface PerceptualIssue {
  id: string; // "piss_" + 16 hex
  revisionId: string;
  category: "visual" | "typography" | "composition" | "motion" | "audio" | "caption" | "temporal";
  severity: "info" | "warning" | "error" | "fatal";
  code: string;
  message: string;
  timeRange?: { start: number; end: number };
  affectedLayerIds: string[];
  observationIds: string[];
  evidence?: Record<string, unknown>;
  repairable: boolean;
  deterministicHash: string;
}
```

---

## 3. Algoritmos de Análisis Perceptual

1. **Contraste de Texto (`ContrastAnalyzer`):**
   $$\text{ContrastRatio} = \frac{L_{\text{foreground}} + 0.05}{L_{\text{background}} + 0.05}$$
   Donde $L = 0.2126 \cdot R + 0.7152 \cdot G + 0.0722 \cdot B$.
2. **Colisiones Espaciales (`CollisionAnalyzer`):**
   Intersección de bounding boxes orientados (AABB/OBB) entre capas de texto, subtítulos e íconos:
   $$\text{IoU} = \frac{\text{Área}(A \cap B)}{\text{Área}(A \cup B)} > 0 \implies \text{TEXT\_COLLISION}$$
3. **Composición y Centro de Masa (`CompositionAnalyzer`):**
   $$x_{\text{cm}} = \frac{\sum A_i \cdot x_i}{\sum A_i}, \quad y_{\text{cm}} = \frac{\sum A_i \cdot y_i}{\sum A_i}, \quad \text{VisualDensity} = \frac{\sum A_i}{\text{CanvasArea}}$$
4. **Detección de Flashes (`FlashDetector`):**
   $$\Delta L = |L(t_{n+1}) - L(t_n)| > 0.6 \quad \text{con frecuencia} \ge 3\text{Hz} \implies \text{FLASH\_INTENSITY\_HIGH}$$
5. **Picos y Recorte de Audio (`ClippingAnalyzer`):**
   $$\text{sample} \ge 0.999 \implies \text{AUDIO\_CLIPPING}$$
6. **Comparador de Renders (`RenderComparator`):**
   $$\text{MeanError} = \frac{1}{W \cdot H} \sum |P_{\text{expected}} - P_{\text{rendered}}|$$

---

## 4. Jerarquía de Errores Tipados (`src/perceptual/errors/`)
- `PerceptualAnalysisError` (base)
- `PerceptualInputError`
- `UnsupportedAnalysisError`
- `PerceptualEvidenceError`
- `PerceptualThresholdError`
- `RenderComparisonError`
- `PerceptualCacheError`

---

## 5. Estrategia de Pruebas de 7 Capas
1. **Capa 1 (Visual & Collision Analyzers):** Colisiones totales, parciales, bordes tangentes, cálculo de centro de masa y densidad de canvas.
2. **Capa 2 (Typography & Contrast Analyzers):** Contraste WCAG ($< 4.5:1$), texto fuera de safe zones, overflow tipográfico y legibilidad.
3. **Capa 3 (Motion & Flash Analyzers):** Presupuesto de movimiento excedido, flashes abruptos y discontinuidad temporal en cortes.
4. **Capa 4 (Audio Perceptual QA):** Picos, clipping $> 0\text{dBFS}$, silencios accidentales y desbalance estéreo.
5. **Capa 5 (RenderComparator & PerceptualDiff):** Comparación frame a frame y detección determinista de píxeles alterados.
6. **Capa 6 (Invariantes & Property-Based Testing `fast-check`):** No mutación de la IR durante el análisis, $\text{scores} \in [0, 100]$, determinismo cross-process.
7. **Capa 7 (E2E & Benchmarks):** Pipeline Job $\to$ Render $\to$ PerceptualQA $\to$ Repair ChangeSet $\to$ Re-QA; benchmarks para 1,000 frames y 10,000 captions.
