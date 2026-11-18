# Documento de Diseño Técnico: Fase 18 — Production Runtime, Project Persistence, Validation & Deterministic Execution

**Versión:** `v1.8.0-design`  
**Estado:** APROBADO PARA IMPLEMENTACIÓN  
**Fecha:** 2026-08-26  

---

## 1. Diagrama de Arquitectura y Flujo de Control

```mermaid
flowchart TD
    subgraph Client / AI Agent
        Agent[LLM Agent / Claude / Cursor]
    end

    subgraph MCP Layer
        McpServer[McpServer / Stdio Transport]
        McpTools[MCP Tools: create, open, save, diff, restore, validate]
        McpResources[MCP Resources: runtime://health, project://{id}]
    end

    subgraph Runtime Control Plane
        Runtime[ProjectRuntime Facade]
        Session[ProjectSession: Defensive Clone]
        TxManager[ProjectTransaction: BEGIN / COMMIT / ROLLBACK]
        LockMgr[LockManager: projectId Concurrency Lock]
        OpMgr[OperationManager: CancellationToken]
        DiffEngine[ProjectDiff: Semantic & Structural]
    end

    subgraph Validation & Health
        Validator[RuntimeValidator: Multi-Layer 6-Stage]
        RefIntegrity[ReferentialIntegrityValidator]
        ResValidator[ResourceValidator & Limits]
        DetValidator[DeterminismValidator]
        HealthVal[ProjectHealthValidator & HealthReport]
    end

    subgraph Persistence & Storage
        Repo[ProjectRepository]
        RevMgr[RevisionManager: rev_000001...]
        Recovery[ProjectRecovery & Journal]
        Serializer[ProjectSerializer: Canonical JSON & SHA-256]
        Storage[StorageAdapter: FileSystem / Memory]
    end

    subgraph Canonical IR
        IR[Canonical Project IR: Composition, Elements, Captions]
        Eval[Evaluate: t -> FrameState]
        Exporters[AE JSX / FCPXML / EDL Exporters]
    end

    Agent -->|MCP Protocol| McpServer
    McpServer --> McpTools
    McpServer --> McpResources
    McpTools --> Runtime
    McpResources --> Runtime

    Runtime --> Session
    Runtime --> Repo
    Runtime --> LockMgr
    Runtime --> Validator

    Session --> TxManager
    Session --> DiffEngine
    Session --> OpMgr

    TxManager --> Validator
    TxManager --> Serializer
    TxManager --> Repo

    Repo --> RevMgr
    Repo --> Recovery
    Repo --> Storage

    Session --> IR
    IR --> Eval
    IR --> Exporters
```

---

## 2. Definición Formal de Interfaces y Tipos Clave

### 2.1. ProjectEnvelope
```typescript
export interface ProjectEnvelope<T = unknown> {
  schemaVersion: string;
  engineVersion: string;
  projectId: string;
  revisionId: string;
  createdAt: string;       // Metadata operacional
  updatedAt: string;       // Metadata operacional
  contentHash: string;     // SHA-256 sobre canonicalizeProject(project)
  project: T;              // Canonical Project IR serializada
  metadata: {
    name: string;
    description?: string;
    author?: string;
    tags?: string[];
    custom?: Record<string, unknown>;
  };
  migrations?: {
    originalSchemaVersion: string;
    migratedAt: string;
    steps: string[];
  };
}
```

### 2.2. Protocolo de Transacciones Atómicas
```typescript
interface ProjectTransaction<T> {
  execute(
    session: ProjectSession,
    mutation: (project: CanonicalProjectIR) => Promise<T> | T,
    options?: { baseRevisionId?: string; description?: string }
  ): Promise<{ result: T; newRevisionId: string; envelope: ProjectEnvelope }>;
}
```

### 2.3. Almacenamiento Seguro
- **`StorageAdapter`:** `read(key)`, `write(key, data)`, `delete(key)`, `exists(key)`, `list(prefix)`.
- **`FileSystemStorageAdapter`:** Escrituras atómicas con sufijo temporal `.tmp.${pid}.${timestamp}`, `fs.flush`, verificación de checksum y renombrado atómico `fs.rename`. Confinamiento estricto en `storageRoot`.

---

## 3. Matriz de Validación de 6 Capas

| Capa | Validador | Responsabilidad |
|---|---|---|
| **1. Schema** | `RuntimeValidator` | Validación Zod contra esquema de envelope y proyecto |
| **2. Resources** | `ResourceValidator` | Límites de nodos, capas ($< 5000$), keyframes ($< 100,000$), longitud de texto |
| **3. Referential**| `ReferentialIntegrityValidator` | Enlaces `parentId`, IDs de assets en `AssetRegistry`, pistas NLE |
| **4. Temporal** | `RuntimeValidator` | Invariantes $t_{\text{start}} \le t_{\text{end}}$, duraciones finitas $> 0$, framerates estándar |
| **5. Assets** | `RuntimeValidator` | Checksum SHA-256 de archivos multimedia referenciados |
| **6. Determinismo**| `DeterminismValidator` | Repetibilidad $\text{Evaluate}(t)_1 \equiv \text{Evaluate}(t)_2 \equiv \text{Evaluate}(t)_3$ |

---

## 4. Estrategia de Migración e Idempotencia
- `MigrationRegistry` registra transformadores con firma `(project: any) => any`.
- `MigrationRunner` encadena transformaciones secuenciales: $v1 \to v2 \to v3$.
- **Idempotencia:** Ejecutar `migrate(migrate(p))` produce exactamente la misma IR y hash que `migrate(p)`.
- **Tolerancia a Fallos:** Si falla una etapa intermedia, el proyecto original no sufre mutaciones.

---

## 5. Estrategia de Testing (7 Capas)
1. Unit Tests (Serializer, Envelope, LockManager, Diff, CancellationToken).
2. Integration Tests (ProjectRepository + FileSystemStorageAdapter + Transacciones).
3. Concurrency Tests (10 lectores concurrentes, exclusión mutua de escritores, detección de stale locks).
4. Failure Simulation Tests (Simulación de crashes en escritura, journals incompletos, corrupción de JSON).
5. Property-Based Testing (`fast-check` sobre proyectos aleatorios: `serialize -> deserialize = identity`).
6. Benchmarks (Mediciones de latencia en save, load, hash, diff, restore para 10, 100 y 1,000 capas).
7. Full Regression (Verificación de los 514 tests de Fases 1–17 al 100% en verde).
