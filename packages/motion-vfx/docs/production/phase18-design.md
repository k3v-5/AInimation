# Diseño Técnico: Fase 18 — Production Orchestration, Revision Control & Render QA (v1.8.0)

## 1. Contratos y Tipos Principales

### 1.1. ProductionProject
```typescript
export interface ProductionProject {
  projectId: string;
  schemaVersion: string;
  title?: string;
  rootRevisionId: string;
  currentRevisionId: string;
  createdFrom: {
    scriptHash?: string;
    seed?: number;
    configurationHash: string;
  };
  metadata: {
    createdBy: string;
    engineVersion: string;
  };
}
```

### 1.2. ProductionRevision
```typescript
export interface ProductionRevision {
  projectId: string;
  revisionId: string;
  parentRevisionId?: string;
  revisionNumber: number;
  ir: Record<string, unknown>; // Canonical Project IR
  irHash: string;              // SHA-256 de canonicalize(ir)
  operationLog: ProductionOperation[];
  createdBy: string;
  metadata: {
    engineVersion: string;
    schemaVersion: string;
  };
}
```

### 1.3. ProductionOperation
```typescript
export interface ProductionOperationBase {
  operationId: string; // hash(parentRevisionId + type + targetId + canonical(parameters))
  type: string;
  targetId: string;
  parameters: unknown;
  deterministicHash: string;
}

export type ProductionOperation =
  | UpdateCaptionStyleOperation
  | UpdateLayerPropertyOperation
  | MoveClipOperation
  | TrimClipOperation
  | AddLayerOperation
  | RemoveLayerOperation
  | ReplaceAssetOperation
  | UpdateCompositionSettingsOperation
  | ApplyPresetOperation;
```

### 1.4. ProductionCheckpoint
```typescript
export interface ProductionCheckpoint {
  checkpointId: string;
  projectId: string;
  revisionId: string;
  label: string;
  revisionHash: string;
  createdAt?: string; // Metadata operacional excluida del hash de identidad
}
```

### 1.5. Render QA & QARules
```typescript
export enum QASeverity {
  INFO = "info",
  WARNING = "warning",
  ERROR = "error",
  FATAL = "fatal",
}

export interface QAIssue {
  ruleId: string;
  severity: QASeverity;
  time?: number;
  targetId?: string;
  message: string;
  diagnostics: Record<string, unknown>;
  deterministicId: string;
}

export interface QARule {
  id: string;
  severity: QASeverity;
  check(frame: unknown, context: QAContext): QAIssue[];
}
```

---

## 2. Flujo del Production Pipeline

$$\text{LOAD} \to \text{VALIDATE} \to \text{RESOLVE ASSETS} \to \text{EVALUATE} \to \text{QA} \to \text{EXPORT} \to \text{VERIFY OUTPUT} \to \text{MANIFEST}$$

- **Dry-Run:** En modo `dryRun: true`, se ejecutan todas las validaciones, evaluaciones de QA y cálculo de hashes sin escribir archivos de salida en disco ni modificar estado permanente.
- **Rollback:** $rev_1 \to rev_2 \to rev_3 \xrightarrow{\text{rollback } rev_1} rev_4$, donde $rev_4.ir \equiv rev_1.ir$, $rev_4.parentRevisionId = rev_3$.
