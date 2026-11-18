# Documento de Diseño Técnico: Fase 24 — Distributed Production Orchestration, Multi-Agent Swarm & Elastic Resource Scheduling (v2.4.0)

## 1. Arquitectura en Capas

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Control Plane                        │
│   (start_distributed_production, scale_workers, swarm)      │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                  DistributedOrchestrator                    │
│      (SwarmCoordinator + TaskPlanner + ElasticScheduler)     │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
┌──────────────▼──────────────┐┌──────────────▼───────────────┐
│     Multi-Agent Swarm       ││   Elastic Resource Scheduler │
│(Director, Editor, Motion,   ││(WorkerPool, Leases, Stealing,│
│ Audio, QA, ThreeWayMerge)   ││ LoadBalancer, Heartbeats)    │
└──────────────┬──────────────┘└──────────────┬───────────────┘
               │                              │
┌──────────────▼──────────────────────────────▼───────────────┐
│             MessageTransport & TaskDAG Execution            │
│       (InMemoryTransport, LocalIPC, TransportEnvelope)      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Contratos y Schemas

### 2.1 `DistributedJob` & `TaskDAG`
```typescript
export interface DistributedJob {
  jobId: string; // "djob_" + 16 hex
  projectId: string;
  briefHash: string;
  baselineRevisionId: string;
  status: "created" | "planning" | "dispatching" | "executing" | "merging" | "completed" | "failed" | "cancelled";
  taskDAG: TaskDAGDefinition;
  allocatedWorkers: number;
  deterministicHash: string;
}

export interface TaskDefinition {
  taskId: string; // "task_" + 16 hex
  jobId: string;
  type: "plan_story" | "edit_timeline" | "design_motion" | "mix_audio" | "render_chunk" | "perceptual_qa" | "mux_export";
  dependencies: string[]; // taskIds
  payload: Record<string, unknown>;
  retryPolicy: {
    maxAttempts: number;
    timeoutMs: number;
    backoffStrategy: "fixed" | "exponential";
  };
  idempotencyKey: string;
}
```

### 2.2 `AgentProposal` & `ThreeWayMergeArbiter`
```typescript
export interface AgentProposal {
  proposalId: string;
  agentRole: "director" | "editor" | "motion" | "audio" | "qa_critic";
  baseRevisionId: string;
  changeSet: ChangeSet;
  confidence: number;
  rationale: string;
  deterministicHash: string;
}
```

---

## 3. Identidades Criptográficas y Hashing

1. **`jobId`:** $\text{SHA256}(\text{canonicalize}(\{\text{brief}, \text{baselineRevisionId}, \text{seed}, \text{engineVersion}\}))[0..16]$
2. **`taskId`:** $\text{SHA256}(\text{canonicalize}(\{\text{jobId}, \text{type}, \text{dependencies}, \text{payload}\}))[0..16]$
3. **`leaseId`:** $\text{SHA256}(\text{canonicalize}(\{\text{taskId}, \text{workerId}, \text{attemptNumber}\}))[0..16]$
4. **`proposalId`:** $\text{SHA256}(\text{canonicalize}(\{\text{agentRole}, \text{baseRevisionId}, \text{changeSet}\}))[0..16]$

---

## 4. Jerarquía de Errores Tipados (`src/distributed/core/DistributedErrors.ts`)
- `DistributedError` (base)
- `TaskDAGCycleError`
- `TaskExecutionTimeoutError`
- `TaskLeaseExpiredError`
- `WorkerCapacityExceededError`
- `WorkerUnavailableError`
- `ProposalConflictError`
- `SwarmCoordinationError`
- `DistributedSerializationError`
- `DistributedIntegrityError`
- `TaskNotFoundError`
- `JobNotFoundError`
- `DistributedEquivalenceError`
- `WorkStealingError`
- `TransportError`

---

## 5. Estrategia de Pruebas de 7 Capas
1. **Capa 1 (Modelos, Schemas & Hashes):** Validación Zod estricta, hashes canónicos y tipado seguro.
2. **Capa 2 (TaskDAG & Scheduler Topológico):** Detección de ciclos (`TaskDAGCycleError`), ordenamiento topológico determinista.
3. **Capa 3 (Swarm Coordination & Three-Way Merge):** Concurrencia de agentes y fusión limpia de propuestas ortogonales.
4. **Capa 4 (Worker Pool, Leases & Crash Recovery):** Caducidad de leases por falta de heartbeats y reasignación limpia.
5. **Capa 5 (Equivalencia Distribuida):** $\text{Run}(1\text{ worker}) \equiv \text{Run}(4\text{ workers})$.
6. **Capa 6 (Invariantes & Property-Based Testing `fast-check`):** Estabilidad de hashes ante permutación de workers y ausencia de deadlocks.
7. **Capa 7 (E2E & Benchmarks de Escalabilidad):** Pipeline distribuido completo y aceleración lineal ($S \ge 3.6\times$).
