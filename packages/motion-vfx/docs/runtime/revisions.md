# Gestor de Revisiones y Concurrencia Optimista (Fase 18)

## Control de Revisiones
- Formato secuencial atómico: `rev_000001`, `rev_000002`, `rev_000003`...
- Concurrencia optimista mediante `baseRevisionId`: Si la versión HEAD no coincide, se dispara `RevisionConflictError`.
- **Restauración no destructiva:** Restaurar `rev_000001` cuando la actual es `rev_000003` crea `rev_000004` con el contenido restaurado, manteniendo todo el historial intacto.
