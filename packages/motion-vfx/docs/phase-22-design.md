# Documento de Diseño Técnico: Fase 22 — Deterministic Creative Optimization, A/B Variants & Production Intelligence (v2.2.0)

## 1. Arquitectura y Flujo de Optimización

```
                    ┌─────────────────────────┐
                    │    CreativeExperiment   │
                    │ (ParameterSpace & Policy)│
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    VariantGenerator     │
                    │ (Grid, Pairwise, Random)│
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Variant Evaluation   │
                    │   (QA Engine + Metrics) │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Creative Scoring     │
                    │(Hook, Pacing, Complexity)│
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Variant Comparator    │
                    │ (Pareto, Regressions)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Winner Selection     │
                    │   (Tie-Break Policy)    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   ExperimentManifest    │
                    │  (Deterministic Report) │
                    └─────────────────────────┘
```

---

## 2. Contratos y Modelos de Datos

### 2.1 `CreativeExperiment`
```typescript
export interface CreativeExperiment {
  id: string; // "exp_" + 16 hex
  projectId: string;
  baselineRevisionId: string;
  name: string;
  parameterSpace: ParameterSpace;
  strategy: "grid" | "pairwise" | "random" | "coordinate_descent";
  maxVariants: number;
  maxIterations: number;
  seed: number;
  weights: ScoreWeights;
  policy: OptimizationPolicy;
  status: "created" | "validating" | "generating" | "evaluating" | "comparing" | "completed" | "cancelled" | "failed";
}
```

### 2.2 `ParameterSpace` & `ParameterDefinition`
```typescript
export type ParameterType = "number" | "integer" | "boolean" | "string" | "enum" | "color" | "duration" | "percentage";

export interface ParameterDefinition {
  path: string; // e.g. "captions.style.fontSize"
  type: ParameterType;
  values?: unknown[];
  min?: number;
  max?: number;
  step?: number;
  defaultValue?: unknown;
}

export interface ParameterSpace {
  parameters: ParameterDefinition[];
  constraints?: ParameterConstraint[];
}
```

### 2.3 `Variant`
```typescript
export interface Variant {
  variantId: string; // "var_" + 16 hex
  experimentId: string;
  parentRevisionId: string;
  revisionId: string;
  parameters: Record<string, unknown>;
  changeSet: ChangeSet;
  irHash: string;
  qaScore: number;
  qaValid: boolean;
  metrics: Record<string, MetricResult>;
  creativeScore: number;
  complexityPenalty: number;
  finalScore: number;
  status: "generated" | "evaluated" | "invalid" | "pareto_optimal" | "winner";
}
```

---

## 3. Fórmulas de Scoring y Penalización de Complejidad

### 3.1 `CreativeScore`
$$\text{CreativeScore} = w_{\text{hook}} \cdot M_{\text{hook}} + w_{\text{pacing}} \cdot M_{\text{pacing}} + w_{\text{caption}} \cdot M_{\text{caption}} + w_{\text{audio}} \cdot M_{\text{audio}} + w_{\text{visual}} \cdot M_{\text{visual}} + w_{\text{motion}} \cdot M_{\text{motion}} + w_{\text{safety}} \cdot M_{\text{safety}}$$
Donde $\sum w_i = 1$ y cada $M_i \in [0, 100]$.

### 3.2 `ComplexityPenalty`
$$\text{ComplexityPenalty} = \min\left(15, 0.05 \cdot N_{\text{layers}} + 0.02 \cdot N_{\text{keyframes}} + 0.1 \cdot N_{\text{effects}}\right)$$

### 3.3 `FinalScore`
$$\text{FinalScore} = \begin{cases} 0 & \text{si } \text{qaValid} = \text{false} \\ \max\left(0, \text{CreativeScore} - \text{ComplexityPenalty}\right) & \text{si } \text{qaValid} = \text{true} \end{cases}$$

---

## 4. Estrategias de Generación Determinista

1. **`GridSearchStrategy`:** Producto cartesiano acotado a `maxVariants`.
2. **`PairwiseStrategy`:** Cobertura determinista de todos los pares de parámetros $(p_i, p_j)$.
3. **`RandomSearchStrategy`:** PRNG sembrado determinista con $\text{seed} + \text{variantIndex} \cdot 1000 + \text{paramIndex}$.
4. **`CoordinateDescentStrategy`:** Optimización unidimensional iterativa por coordenada con límite de iteraciones.

---

## 5. Jerarquía de Errores Tipados (`src/optimization/errors/`)
- `OptimizationError` (base)
- `OptimizationValidationError`
- `ParameterSpaceError`
- `InvalidParameterValueError`
- `ParameterConstraintError`
- `VariantGenerationError`
- `VariantLimitExceededError`
- `ExperimentStateTransitionError`
- `MetricEvaluationError`
- `CreativeScoreError`
- `VariantComparisonError`
- `RegressionDetectedError`
- `OptimizationTimeoutError`
- `OptimizationCancelledError`
- `OptimizationDeterminismError`
- `ExperimentSerializationError`

---

## 6. Estrategia de Pruebas de 7 Capas
1. **Capa 1 (ParameterSpace & Schemas):** Validación Zod estricta, rechazo de rangos invertidos o valores incompatibles.
2. **Capa 2 (Estrategias de Búsqueda):** Grid, Pairwise, Random (sembrado determinista) y Coordinate Descent.
3. **Capa 3 (Creative Metrics & Scoring):** Pacing, Hook, Captions, Audio, Motion, Visual Density y penalización de complejidad.
4. **Capa 4 (Comparación, Pareto & Regresiones):** Detección de regresiones frente al baseline y cálculo de la frontera de Pareto.
5. **Capa 5 (Experimentos A/B & Asignación Determinista):** Asignación determinista $\text{hash}(\text{subjectId} + \text{experimentId})$.
6. **Capa 6 (Invariantes & Property-Based Testing `fast-check`):** No mutación del baseline, $\text{same seed} \implies \text{same variants}$, $\text{score} \in [0, 100]$.
7. **Capa 7 (E2E & Benchmarks):** Pipeline completo Brief $\to$ Baseline $\to$ Experiment $\to$ Variants $\to$ Ranking $\to$ Winner; benchmarks hasta 1,000 variantes.
