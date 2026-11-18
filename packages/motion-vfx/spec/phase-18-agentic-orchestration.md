# Especificación Técnica: Fase 18 — Agentic Video Orchestration, Project Persistence & Production Workflows (v1.8.0)

## 0. Propósito y Alcance

La **Fase 18** convierte el motor audiovisual determinista de las Fases 1–17 en una plataforma de producción audiovisual persistente, versionada (con grafo DAG no lineal, branching y merge 3-way) y resiliente (workflows asíncronos con checkpoints y recuperación ante caídas), operable de extremo a extremo por agentes autónomos de IA.

---

## 1. Módulos Implementados

### 1.1 `src/persistence/`
- **`ProjectStore`**: Interfaz unificada de almacenamiento de proyectos y revisiones.
- **`MemoryProjectStore`**: Almacén en memoria volátil de alta velocidad.
- **`FileProjectStore`**: Almacén en disco con escrituras atómicas (`.tmp` $\to$ `fsync` $\to$ `rename`) y sandboxing con `PathSanitizer`.
- **`ProjectSerializer` / `ProjectDeserializer`**: Serialización canónica determinista y deserialización a instancias del core.
- **`ProjectMigration`**: Migraciones secuenciales de esquemas v0.1.0 $\to$ v0.2.0 $\to$ v1.8.0.

### 1.2 `src/revisions/`
- **`RevisionId`**: Identificadores criptográficos reproducibles derivados por hashing SHA-256.
- **`RevisionGraph`**: DAG no lineal con soporte de branching, ancestría, descendencia y consultas de linaje.
- **`RevisionDiff`**: Motor de diferencias semánticas entre estados de la IR.
- **`RevisionPatch`**: Aplicación y reversión de parches cumpliendo $\text{reversePatch}(\text{applyPatch}(P, \Delta), \Delta) \equiv P$.
- **`RevisionMerge`**: Fusión 3-way no conflictiva y detección de `RevisionConflict`.
- **`RevisionManager`**: Gestor de alto nivel para creación, branching, merge, undo y restore.

### 1.3 `src/workflows/`
- **`WorkflowDefinition`**: Definición tipada de pasos y dependencias DAG.
- **`WorkflowPlanner`**: Ordenamiento topológico y validación de ciclos.
- **`WorkflowEngine`**: Ejecución paso a paso con políticas de reintento (`RetryPolicy`) y cancelación.
- **`WorkflowCheckpoint` / `WorkflowRecovery`**: Persistencia de checkpoints y reanudación sin repetir pasos completados.

### 1.4 `src/agent/`
- **`AgentSession`**: Sesión autónoma con concurrencia optimista (`RevisionConflictError` ante desincronización de HEAD).
- **`AgentPolicy`**: Reglas y restricciones de acciones permitidas.
- **`AgentMemory`**: Registro auditable de observaciones y decisiones.

### 1.5 `src/mcp/`
- **16 Herramientas MCP**: `create_project`, `open_project`, `save_project`, `get_project`, `list_projects`, `create_revision`, `get_revision`, `list_revisions`, `diff_revisions`, `restore_revision`, `undo_revision`, `run_workflow`, `get_workflow_status`, `cancel_workflow`, `resume_workflow`, `validate_project`.
- **Recursos Declarativos**: `projects://`, `projects://{id}`, `projects://{id}/revisions`, `projects://{id}/revisions/{revId}`, `workflows://{id}`.

---

## 2. Invariantes Verificados
- **100% Determinismo:** Hashes invariantes ante permutación de claves.
- **Inmutabilidad:** Las operaciones `undo` y `restore` nunca destruyen revisiones pasadas; crean nuevas revisiones en el grafo.
- **Integridad de Recuperación:** Reanudación precisa desde el último checkpoint confirmado.
- **Seguridad Sandbox:** Rechazo absoluto de path traversal en rutas de proyecto y exportación.
