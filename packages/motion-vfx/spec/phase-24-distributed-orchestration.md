# Especificación Técnica Maestra: Fase 24 — Distributed Production Orchestration, Multi-Agent Swarm & Elastic Resource Scheduling (v2.4.0)

## 0. Propósito y Principio Rector

La **Fase 24** extiende la plataforma consolidada en el **Milestone 23** permitiendo la **ejecución distribuida y paralela de producciones audiovisuales complejas mediante un enjambre coordinado de agentes especializados (Multi-Agent Swarm) y un planificador de recursos elástico (Elastic Resource Scheduler)**, preservando en todo momento el **determinismo criptográfico absoluto**, la inmutabilidad de la IR canónica y la idempotencia de las tareas.

```
                         ┌─────────────────────────────┐
                         │   Swarm Production Brief    │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │    Distributed Orchestrator │
                         │    & Swarm Coordinator      │
                         └──────────────┬──────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
  ┌──────────────────┐         ┌──────────────────┐         ┌──────────────────┐
  │  Director Agent  │         │   Editor Agent   │         │ Motion/FX Agent  │
  └────────┬─────────┘         └────────┬─────────┘         └────────┬─────────┘
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        │ (ChangeSets Concurrentes)
                         ┌──────────────▼──────────────┐
                         │   Three-Way Merge Arbiter   │
                         │    & Revision Engine        │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │  Elastic Resource Scheduler │
                         │  (Task DAG & Worker Pool)   │
                         └──────────────┬──────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
    [ Worker 1: Render ]      [ Worker 2: Audio/Mix ]     [ Worker 3: Perceptual QA ]
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │   Distributed Delivery      │
                         │   & Consolidated Manifest   │
                         └─────────────────────────────┘
```

### 🛡️ Invariantes No Negociables
1. **La IR Canónica es la ÚNICA fuente de verdad:** Ningún agente ni worker modifica directamente el estado sin emitir un `ChangeSet` validado y fusionado determinísticamente por el `MergeArbiter`.
2. **Equivalencia Distribuida:**
   $$\text{Run}(\text{1 worker local}) \equiv \text{Run}(N\text{ workers distribuidos})$$
   El paralelismo y el orden de llegada físico de paquetes de red o threads no pueden alterar el resultado lógico, los hashes ni los manifiestos de salida.
3. **Idempotencia de Tareas Distribuidas:** Toda tarea distribuida posee una identidad criptográfica determinista `taskId`. La reejecución de una tarea completada devuelve el resultado memoizado sin duplicar cómputo ni efectos colaterales.
4. **Leases y Heartbeats Sin Deadlocks:** Los workers adquieren tareas con arrendamientos lógicos temporizados (`TaskLease`). Si un worker colapsa o deja de emitir heartbeats, la tarea se reasigna limpiamente según la `RetryPolicy`.
5. **Cero Dependencia de Reloj de Sistema:** Ningún timestamp físico participa en identidades, hashes de tareas, revisiones o manifiestos.

---

## 1. Objetivos de la Fase 24

Al finalizar la versión v2.4.0, el sistema deberá:
1. Descomponer una producción compleja en un grafo de tareas distribuidas (`TaskDAG`).
2. Coordinar un enjambre de agentes especializados (`Director`, `Editor`, `MotionDesigner`, `AudioEngineer`, `QACritic`).
3. Fusionar modificaciones concurrentes de agentes mediante el `ThreeWayMergeArbiter` resolviendo colisiones ortogonales automáticamente.
4. Distribuir la carga de renderizado, análisis perceptual, mezcla de audio y exportación entre un pool elástico de workers.
5. Gestionar fallos de workers con reintentos deterministas y migración transparente de tareas.
6. Monitorear el progreso distribuido con telemetría en tiempo real y métricas de throughput.
7. Exponer la orquestación distribuida mediante 7 nuevas herramientas MCP y 8 recursos declarativos.
8. Mantener el 100% de compatibilidad con las 557 pruebas previas de las Fases 1–23.

---

## 2. Fuera de Alcance

La Fase 24 NO debe implementar:
- Dependencia obligatoria de clusters propietarios (Kubernetes, AWS Lambda, Redis); el sistema debe incluir backends locales / in-memory y transporte tipado agnóstico.
- LLMs externos obligatorios para el scheduler (toda la planificación de tareas y merge es puramente determinista y algorítmica).
- Modificación destructiva de revisiones pasadas.
- Nuevos efectos visuales o nuevos tipos de capas.

---

## 3. Arquitectura de Módulos Propuesta (`src/distributed/`)

```
src/
  distributed/
    core/
      DistributedJob.ts          # Modelo y ciclo de vida de producción distribuida
      DistributedConfig.ts       # Configuración de concurrencia, leases y timeouts
      DistributedContext.ts      # Contexto inmutable compartido
      DistributedResult.ts       # Resultado consolidado con manifiestos
      DistributedErrors.ts       # Jerarquía de 15 errores tipados

    tasks/
      TaskDefinition.ts          # Definición tipada de tarea distribuida
      TaskDAG.ts                 # Grafo acíclico de dependencias entre tareas
      TaskPlanner.ts             # Compilador de ProductionPlan a TaskDAG
      TaskLease.ts               # Arrendamiento de tarea con heartbeat
      TaskResult.ts              # Resultado serializable con payloadHash

    swarm/
      AgentRole.ts               # "director" | "editor" | "motion" | "audio" | "qa_critic"
      SwarmAgent.ts              # Interfaz base de agente enjambre
      SwarmCoordinator.ts        # Orquestador del ciclo de vida del enjambre
      AgentMessage.ts            # Mensajería tipada entre agentes
      AgentProposal.ts           # Propuesta de ChangeSet emitida por un agente
      ThreeWayMergeArbiter.ts    # Fusión 3-way determinista de propuestas concurrentes

    scheduler/
      ElasticScheduler.ts        # Planificador elástico de tareas
      WorkerPool.ts              # Gestión de workers registrados y capacidades
      WorkerNode.ts              # Abstracción de nodo de trabajo
      LoadBalancer.ts            # Estrategias de balanceo ("least_loaded", "affinity", "round_robin")
      HeartbeatMonitor.ts        # Monitorización de salud de workers y caducidad de leases
      WorkStealingEngine.ts      # Rebalanceo determinista de tareas pendientes

    transport/
      MessageTransport.ts        # Interfaz abstracta de transporte
      InMemoryTransport.ts       # Transporte en memoria para tests y ejecución local
      LocalProcessTransport.ts   # Transporte interproceso IPC
      TransportEnvelope.ts       # Envoltorio de mensajes con checksum SHA-256

    telemetry/
      SwarmTelemetry.ts          # Métricas de throughput, latencia y utilización
      ClusterStatus.ts           # Estado general del clúster de workers
      DistributedEventLog.ts     # Registro monotónico distribuido de eventos

    index.ts                     # Barrel export público

  mcp/
    tools/
      start-distributed-production.ts  # MCP Tool: start_distributed_production
      get-distributed-job-status.ts    # MCP Tool: get_distributed_job_status
      scale-worker-pool.ts             # MCP Tool: scale_worker_pool
      inspect-swarm-decisions.ts       # MCP Tool: inspect_swarm_decisions
      abort-distributed-task.ts        # MCP Tool: abort_distributed_task
      get-cluster-telemetry.ts         # MCP Tool: get_cluster_telemetry
      consolidate-distributed-manifest.ts # MCP Tool: consolidate_distributed_manifest
    resources/
      distributed-resources.ts         # Recursos declarativos: distributed://{jobId}, etc.
```

---

## 4. Modelos de Datos y Schemas Zod

### 4.1 `DistributedJob`
```typescript
export interface DistributedJob {
  jobId: string; // "djob_" + 16 hex
  projectId: string;
  briefHash: string;
  baselineRevisionId: string;
  taskDAG: TaskDAGDefinition;
  allocatedWorkers: number;
  status: "created" | "planning" | "dispatching" | "executing" | "merging" | "completed" | "failed" | "cancelled";
  createdAtLogical: number;
  deterministicHash: string;
}
```

### 4.2 `TaskDefinition`
```typescript
export type TaskType = "plan_story" | "edit_timeline" | "design_motion" | "mix_audio" | "render_chunk" | "perceptual_qa" | "mux_export";

export interface TaskDefinition {
  taskId: string; // "task_" + 16 hex
  jobId: string;
  type: TaskType;
  requiredRole?: AgentRole;
  dependencies: string[]; // taskIds
  payload: Record<string, unknown>;
  expectedOutputSchema: string;
  retryPolicy: {
    maxAttempts: number;
    timeoutMs: number;
    backoffStrategy: "fixed" | "exponential";
  };
  idempotencyKey: string;
}
```

### 4.3 `AgentProposal` & `ThreeWayMergeArbiter`
```typescript
export interface AgentProposal {
  proposalId: string;
  agentRole: AgentRole;
  baseRevisionId: string;
  changeSet: ChangeSet;
  confidence: number;
  rationale: string;
  deterministicHash: string;
}
```
El `ThreeWayMergeArbiter` combina propuestas no conflictivas sobre propiedades disjuntas (ej. Director modifica escenas, MotionDesigner ajusta transiciones, AudioEngineer balancea pistas) y detecta colisiones directas emitiendo un `ProposalConflictError` con contexto exacto.

---

## 5. Identidades Criptográficas y Hashing Canónico

1. **`jobId`:** $\text{SHA256}(\text{canonicalize}(\{\text{brief}, \text{baselineRevisionId}, \text{config}, \text{seed}\}))[0..16]$
2. **`taskId`:** $\text{SHA256}(\text{canonicalize}(\{\text{jobId}, \text{taskType}, \text{dependencies}, \text{payload}\}))[0..16]$
3. **`leaseId`:** $\text{SHA256}(\text{canonicalize}(\{\text{taskId}, \text{workerId}, \text{attemptNumber}\}))[0..16]$
4. **`proposalId`:** $\text{SHA256}(\text{canonicalize}(\{\text{agentRole}, \text{baseRevisionId}, \text{changeSet}\}))[0..16]$

---

## 6. Herramientas MCP y Recursos Declarativos

### 7 Herramientas MCP
1. `start_distributed_production`: Descompone un brief y lanza la producción en el enjambre distribuido.
2. `get_distributed_job_status`: Consulta el progreso del DAG, tareas activas, leases y workers asignados.
3. `scale_worker_pool`: Ajusta la capacidad elástica del pool de workers disponibles.
4. `inspect_swarm_decisions`: Consulta las propuestas emitidas por cada agente del enjambre y el reporte del `ThreeWayMergeArbiter`.
5. `abort_distributed_task`: Cancela cooperativamente una tarea o rama del DAG sin corromper el estado global.
6. `get_cluster_telemetry`: Emite métricas de utilización de workers, latencia de mensajes y throughput de tareas.
7. `consolidate_distributed_manifest`: Ensambla el `DeliveryManifest` final consolidando los artefactos de todos los workers.

### 8 Recursos MCP Declarativos
- `distributed://{jobId}`: estado general de la producción distribuida.
- `distributed://{jobId}/dag`: visualización del grafo de tareas y dependencias.
- `distributed://{jobId}/tasks/{taskId}`: estado y resultados de una tarea individual.
- `distributed://{jobId}/swarm`: registro de agentes y propuestas emitidas.
- `distributed://{jobId}/telemetry`: telemetría de rendimiento y tiempos.
- `distributed://cluster/workers`: catálogo de workers activos y capacidades.
- `capabilities://distributed`: capacidades del scheduler elástico.
- `policies://distributed`: políticas de retry, leases y arbitraje de merge.

---

## 7. Protocolo de Verificación de 7 Capas

1. **Capa 1: Unit Tests de Modelos y Schemas (`DistributedJob.test.ts`):**
   - Validación Zod estricta, hashes canónicos, rechazo de payloads no conformes.
2. **Capa 2: TaskDAG y Scheduler Topológico (`TaskDAGAndScheduler.test.ts`):**
   - Detección de ciclos en tareas distribuidas (`TaskDAGCycleError`), ordenamiento topológico determinista y resolución de dependencias.
3. **Capa 3: Swarm Coordination & Three-Way Merge (`SwarmAndMergeArbiter.test.ts`):**
   - Concurrencia de agentes (`Director` + `Motion` + `Audio`), fusión 3-way limpia de propuestas ortogonales y detección de conflictos.
4. **Capa 4: Worker Pool, Leases & Crash Recovery (`WorkerPoolAndLeases.test.ts`):**
   - Asignación de leases, timeout por falta de heartbeats, reasignación automática sin pérdida de datos e idempotencia de tareas.
5. **Capa 5: Equivalencia Distribuida (`DistributedEquivalence.test.ts`):**
   - $\text{Run}(1\text{ worker local}) \equiv \text{Run}(4\text{ workers distribuidos})$ (idénticos hashes de IR, artefactos y manifiestos).
6. **Capa 6: Property-Based Testing con `fast-check` (`DistributedPBT.test.ts`):**
   - Invariantes de no-mutación, estabilidad de hashes ante permutación de workers y ausencia de deadlocks en el DAG.
7. **Capa 7: End-to-End & Benchmarks de Escalabilidad (`DistributedBenchmarks.test.ts`):**
   - Pipeline distribuido completo Brief $\to$ Swarm $\to$ Merge $\to$ Distributed Render $\to$ Consolidated Manifest.
   - Rendimiento para 10, 100 y 1,000 tareas distribuidas con aceleración casi lineal ($S \ge 3.6\times$ para 4 workers).
   - Verificación del 100% de los 557 tests existentes de Fases 1–23 en verde.

---

## 8. Definition of Done y Criterios de Aceptación

La Fase 24 se considerará completada únicamente cuando:
- [x] El `TaskPlanner` y `ElasticScheduler` compilen y ordenen DAGs de tareas de forma 100% determinista.
- [x] El `ThreeWayMergeArbiter` fusione propuestas concurrentes de agentes sin introducir inconsistencias en la IR.
- [x] Los workers manejen leases con heartbeats y se recuperen limpiamente ante colapsos simulados.
- [x] La equivalencia local vs distribuida esté demostrada matemáticamente en los tests.
- [x] Las 7 herramientas MCP y 8 recursos declarativos estén operativos y tipados.
- [x] La suite completa de 557 tests previos más las nuevas suites de Fase 24 pasen al 100% en verde.
- [x] Se genere la documentación formal en `docs/distributed/`, `spec/` y reportes de fase.

---

## 9. Protocolo de Ejecución para la IA Implementadora

```
AUDIT (Verificar 557 tests baseline y contratos)
  ↓
DESIGN (Contratos de Swarm, TaskDAG y WorkerPool)
  ↓
SCHEMA & PERSISTENCE (Modelos Zod y Transporte agnóstico)
  ↓
IMPLEMENT CORE (TaskPlanner, ElasticScheduler, MergeArbiter)
  ↓
SWARM AGENTS (Director, Editor, Motion, Audio, QACritic)
  ↓
MCP INTEGRATION (7 Tools & 8 Resources)
  ↓
7-LAYER TESTING (Unit, DAG, Swarm, Leases, Equivalence, PBT, Benchmarks)
  ↓
DOCUMENTATION & FINAL REPORT
```
