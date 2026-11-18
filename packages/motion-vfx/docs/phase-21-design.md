# Documento de Diseño Técnico: Fase 21 — Production Memory, Adaptive Optimization & Deterministic Learning Layer (v2.1.0)

## 1. Arquitectura y Flujo de Información

```
                    ┌─────────────────────────┐
                    │    Production Memory    │
                    │  (MemoryStore & Index)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Similarity Engine    │
                    │   (SimilarityScorer)    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │     Evidence Model      │
                    │   (Pattern / Outcomes)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Recommendation Engine  │
                    │(RecommendationValidator)│
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │ ProductionOrchestrator  │
                    │ (ChangeSet / Revision)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   ProductionAnalytics   │
                    │ (Cohorts, Trends, Regr) │
                    └─────────────────────────┘
```

---

## 2. Contratos y Modelos de Datos

### 2.1 `ProductionMemory`
```typescript
export interface ProductionMemory {
  memoryId: string;
  schemaVersion: string;
  productionId: string;
  revisionId: string;
  projectFingerprint: string;
  contentFingerprint: string;
  briefFingerprint: string;
  styleFingerprint: string;
  metrics: ProductionMetrics;
  qa: {
    score: number;
    issuesCount: number;
    blockingCount: number;
    passedRules: string[];
    failedRules: string[];
  };
  revisions: {
    totalRevisions: number;
    changeSetTypes: string[];
  };
  repairs: {
    appliedStrategies: string[];
    successRate: number;
  };
  tags: string[];
  scope: "global" | "organization" | "project" | "production";
  status: "active" | "deprecated" | "invalidated";
  evidence: string[]; // Evidence IDs
  contentHash: string;
}
```

### 2.2 `ProductionFingerprint`
$$\text{Fingerprint} = \text{SHA256}(\text{canonicalize}(\{\text{aspectRatio}, \text{duration}, \text{fps}, \text{language}, \text{captionStyle}, \text{audioProfile}, \text{visualStyle}\}))[0..16]$$

### 2.3 `SimilarityScore`
$$\text{SimilarityScore} = 0.20 \cdot S_{\text{duration}} + 0.15 \cdot S_{\text{aspectRatio}} + 0.15 \cdot S_{\text{style}} + 0.15 \cdot S_{\text{caption}} + 0.10 \cdot S_{\text{audio}} + 0.10 \cdot S_{\text{motion}} + 0.10 \cdot S_{\text{scene}} + 0.05 \cdot S_{\text{language}}$$

---

## 3. Modelo de Evidencia y Recomendaciones (`EvidenceModel` & `RecommendationEngine`)

```typescript
export interface Evidence {
  evidenceId: string;
  sourceProductionIds: string[];
  sourceIssueIds: string[];
  observations: number;
  successes: number;
  failures: number;
  confidence: number; // successes / observations
  methodology: string;
}

export interface Recommendation {
  recommendationId: string;
  type: "style" | "caption" | "audio" | "motion" | "asset" | "repair" | "performance";
  target: string;
  rationale: string;
  proposedChanges?: Record<string, unknown>;
  evidenceIds: string[];
  confidence: number;
  priority: number;
  status: "suggested" | "accepted" | "rejected" | "applied" | "expired";
  deterministicHash: string;
}
```

---

## 4. Analíticas, Regresiones y Cuellos de Botella (`ProductionAnalytics`)

1. **`QualityMetrics`:** Normalizadas de 0 a 100 para `structural`, `timeline`, `caption`, `audio`, `visual`, `asset` y `export`.
2. **`RegressionDetector`:** Detecta caídas puntuales en dimensiones específicas (ej. caption quality $98 \to 71$) aunque el score global no disminuya.
3. **`BottleneckDetector`:** Identifica etapas con contribución desproporcionada al tiempo de ejecución (ej. export $> 60\%$).

---

## 5. Jerarquía de Errores Tipados (`src/intelligence/errors/`)
- `IntelligenceError` (base)
- `MemoryValidationError`
- `MemorySerializationError`
- `MemoryIntegrityError`
- `MemoryScopeError`
- `MemoryQueryError`
- `SimilarityConfigurationError`
- `RecommendationValidationError`
- `RecommendationEvidenceError`
- `RecommendationExpiredError`
- `RecommendationConflictError`
- `AnalyticsError`
- `ComparisonError`
- `RegressionDetectionError`
- `KnowledgeLifecycleError`

---

## 6. Estrategia de Pruebas de 7 Capas
1. **Capa 1 (Schemas & Envelopes):** Validación Zod estricta, hashes SHA-256, serialización canónica.
2. **Capa 2 (Similarity & Indexing):** Pesos declarativos, normalización en $[0, 1]$, resolución de empates determinista.
3. **Capa 3 (Evidence & Pattern Detection):** Agrupación estadística de issues recurrentes y tasas de éxito de reparaciones.
4. **Capa 4 (Recommendations & Policies):** Validación previa de targets y ChangeSets, rechazo de recomendaciones sin evidencia suficiente (`RecommendationEvidenceError`).
5. **Capa 5 (Analytics, Trends & Regressions):** Detección de regresiones dimensionales y análisis de cohortes.
6. **Capa 6 (Aislamiento de Memoria & Scopes):** Aislamiento estricto de memorias entre proyectos `projectA` vs `projectB`.
7. **Capa 7 (E2E, Property-Based Testing & Benchmarks):** Pipeline completo Brief $\to$ Memory $\to$ Recommendation $\to$ ChangeSet $\to$ QA; benchmarks para 1,000, 10,000 y 100,000 entradas de memoria.
