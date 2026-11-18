# Runtime Architecture: Motion Graphics Engine & MCP (Fase 18)

## 🏛️ Principios de Diseño

El **Runtime de Producción** desacopla el ciclo de vida operacional del motor de edición de su fuente de verdad canónica.

```
                    ┌─────────────────────┐
                    │   LLM / Agent       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    MCP Control      │
                    │       Plane         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Project Runtime   │
                    │                     │
                    │ Sessions            │
                    │ Transactions        │
                    │ Revisions           │
                    │ Locks               │
                    │ Recovery            │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Canonical IR      │
                    │   SINGLE SOURCE     │
                    │     OF TRUTH        │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
        Evaluate(t)        Render            Export
             │                 │                 │
             │                 │        ┌────────┼─────────┐
             │                 │        ▼        ▼         ▼
             │                 │       JSX    FCPXML      EDL
             │                 │
             └────────┬────────┘
                      ▼
               FrameState(t)
```

## Invariantes Centrales
1. **La IR Canónica es la Única Fuente de Verdad:** No existen modelos paralelos ni cachés que alteren el resultado.
2. **Desacoplamiento de Almacenamiento:** Todo acceso a persistencia pasa por `StorageAdapter` y `ProjectRepository`.
3. **Inmutabilidad de Revisiones:** Cada mutación genera una nueva revisión; las revisiones históricas nunca se sobrescriben.
