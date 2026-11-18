# Bloqueos y Concurrencia (Fase 18)

## Exclusión Mutua
- Bloqueo por `projectId` almacenado en `projects/{projectId}/project.lock`.
- Múltiples lectores concurrentes soportados.
- Un solo escritor activo por sesión.
- Manejo de `LockTimeoutError` y expiración automática de locks huérfanos/stale (`LOCK_STALE_AGE_MS = 60s`).
